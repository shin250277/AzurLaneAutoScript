"""Observed name templates with offline Hangul OCR fallback, not CN guesses."""
from pathlib import Path

import cv2
import numpy as np

from module.base.decorator import cached_property
from module.base.utils import crop, load_image
from module.island.data import DIC_ISLAND_ITEM
from module.logger import logger
from module.ocr.ocr import Ocr
from module.ocr.windows_ocr import WindowsKoreanOcr


def confirmed_contrast_name(candidate, reads, known_names):
    return (len(reads) == 3 and reads.count(candidate) >= 2
            and not any(value in known_names and value != candidate for value in reads))


def photometric_agreement(template, observed):
    """Allow small uniform lighting changes, never shape/scale correction.

    Reviewed translucent-card pairs retain >.999 correlation but differ by
    7-9 gray levels. Fit only one gain/offset, with strict residual limits.
    Callers must also require whole-label extent and an unambiguous identity.
    """
    x, y = template.astype(np.float64), observed.astype(np.float64)
    if x.shape != y.shape or not x.size or not np.isfinite(x).all() or not np.isfinite(y).all():
        return False
    centered = x - x.mean()
    variance = (centered * centered).mean()
    if variance < 100:
        return False
    gain = (centered * (y-y.mean())).mean() / variance
    offset = y.mean() - gain*x.mean()
    error = np.abs(y - (gain*x + offset))
    return bool(.9 <= gain <= 1.1 and abs(offset) <= 10
                and error.mean() < 1 and np.percentile(error, 99) < 3)


class KoreanIslandNameOcr(Ocr):
    template_folder = 'assets/kr/island_item_name'
    name_dictionary = DIC_ISLAND_ITEM

    def prepare_fallback(self, frame):
        # Windows OCR can miss Hangul touching the right/bottom crop edge.
        # Keep all observed pixels and add context, rather than altering text.
        padding = ((20, 20), (20, 20)) + ((0, 0),) * (frame.ndim - 2)
        return np.pad(frame, padding, mode='constant', constant_values=255)

    def localized_fallbacks(self, frame):
        """Locate dark text at three levels; keep original glyph pixels/colors."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
        frames = []
        for level in (90, 110, 130):
            y, x = np.where(gray < level)
            if not len(x):
                return []
            frames.append(self.prepare_fallback(frame[
                max(int(y.min()) - 1, 0):min(int(y.max()) + 2, frame.shape[0]),
                max(int(x.min()) - 1, 0):min(int(x.max()) + 2, frame.shape[1])]))
        return frames

    def glyph_fallbacks(self, frame):
        """Exclude short decoration when locating text; keep original pixels."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
        frames = []
        for level in (90, 110, 130):
            _, _, stats, _ = cv2.connectedComponentsWithStats((gray < level).astype(np.uint8), 8)
            boxes = [s for s in stats[1:] if s[3] >= 8 and s[2] >= 2]
            if not boxes:
                return []
            left, top = min(s[0] for s in boxes), min(s[1] for s in boxes)
            right = max(s[0] + s[2] for s in boxes)
            bottom = max(s[1] + s[3] for s in boxes)
            frames.append(self.prepare_fallback(frame[
                max(top-1, 0):min(bottom+1, frame.shape[0]),
                max(left-1, 0):min(right+1, frame.shape[1])]))
        return frames

    @staticmethod
    def complete_label_span(gray, left, right):
        """Reject substring hits when independent glyphs extend beyond them.

        Horizontal card rules are not glyphs. No rescaling or inferred names;
        uncertain backgrounds may reject a match and use the OCR fallback.
        """
        for level in (110, 130, 150):
            _, _, stats, _ = cv2.connectedComponentsWithStats((gray < level).astype(np.uint8), 8)
            boxes = [s for s in stats[1:] if s[3] >= 8 and s[2] >= 2]
            # Existing low-threshold templates can omit faint edge strokes
            # (observed copper label: five pixels). Never allow a full extra
            # Hangul syllable beyond the matched extent.
            if boxes and (min(s[0] for s in boxes) < left - 6
                          or max(s[0] + s[2] for s in boxes) > right + 6):
                return False
        return True

    @staticmethod
    def pixel_exact_match(candidates, errors):
        """Require near-identical observed pixels, not just shape correlation."""
        return bool(candidates and candidates[0][0] > 0.995
                    and errors[candidates[0][1]] < 1.0
                    and all(errors[name] > 5.0 for _, name in candidates[1:]))

    @cached_property
    def mask_references(self):
        return [(self.name_dictionary[int(path.stem.split('_')[0])]['name']['kr'],
                 cv2.cvtColor(load_image(str(path)), cv2.COLOR_RGB2GRAY))
                for path in Path(self.template_folder).glob('*.png')]

    @cached_property
    def templates(self):
        templates = []
        for path in Path(self.template_folder).glob('*.png'):
            gray = cv2.cvtColor(load_image(str(path)), cv2.COLOR_RGB2GRAY)
            exact_only = path.stem.endswith('_selected')
            areas = set()
            # Faint terminal strokes can be above 110 on translucent cards.
            # Add their full extent as another exact-only reference; do not
            # relax identity thresholds or remove the substring guard.
            for level in ((110, 150) if exact_only else (110,)):
                y, x = np.where(gray < level)
                if not len(x):
                    continue
                area = (max(int(y.min())-1, 0), min(int(y.max())+2, gray.shape[0]),
                        max(int(x.min())-2, 0), min(int(x.max())+3, gray.shape[1]))
                if area in areas:
                    continue
                areas.add(area)
                template = cv2.GaussianBlur(gray, (5, 5), 0)[area[0]:area[1], area[2]:area[3]]
                templates.append((self.name_dictionary[int(path.stem.split('_')[0])]['name']['kr'],
                                  template, exact_only))
        return templates

    def ocr(self, image, direct_ocr=False):
        frames = image if direct_ocr else [crop(image, area) for area in self.buttons]
        values = []
        unresolved = []
        fallback_candidates = {}
        shape_candidates = {}
        lighting_candidates = {}
        for index, frame in enumerate(frames):
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
            raw_gray = gray
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            scores = {}
            spans = {}
            errors = {}
            shapes = {}
            lighting = set()
            for name, template, exact_only in self.templates:
                if gray.shape[0] >= template.shape[0] and gray.shape[1] >= template.shape[1]:
                    _, score, _, point = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))
                    if not self.complete_label_span(raw_gray, point[0], point[0] + template.shape[1]):
                        continue
                    observed = gray[point[1]:point[1] + template.shape[0],
                                    point[0]:point[0] + template.shape[1]]
                    error = float(np.abs(observed.astype(np.float32) - template).mean())
                    if exact_only and np.isfinite(score):
                        shapes[name] = max(shapes.get(name, 0), score)
                        if score > .999 and photometric_agreement(template, observed):
                            lighting.add(name)
                    # Selected-card renderings of similar Hangul must not
                    # change fallback candidates on unrelated renderings.
                    if exact_only and not (score > 0.995 and error < 1.0):
                        continue
                    if np.isfinite(score):
                        if score > scores.get(name, 0):
                            scores[name] = score
                            spans[name] = (point[0], point[0] + template.shape[1])
                            observed = gray[point[1]:point[1] + template.shape[0],
                                            point[0]:point[0] + template.shape[1]]
                            errors[name] = float(np.abs(observed.astype(np.float32) - template).mean())
            # Multiple observed scroll renderings of the same name are not
            # competing identities; ambiguity is between different products.
            # A one-character template can match a visually similar syllable
            # inside a complete word (게 versus 개 in 조개). Only suppress the
            # short hit when a strict longer match spatially contains it.
            candidates = sorted(((score, name) for name, score in scores.items()
                                 if not any(name != other and other_score > 0.94
                                            and spans[other][0] <= spans[name][0] + 2
                                            and spans[other][1] >= spans[name][1] - 2
                                            and spans[other][1] - spans[other][0] > spans[name][1] - spans[name][0] + 6
                                            for other, other_score in scores.items())), reverse=True)
            if (candidates and candidates[0][0] > 0.94
                    and (len(candidates) == 1 or candidates[0][0] - candidates[1][0] > 0.10
                         or self.pixel_exact_match(candidates, errors))):
                values.append(candidates[0][1])
            else:
                values.append('')
                unresolved.append(index)
                fallback_candidates[index] = candidates
                shape_candidates[index] = sorted(((v, n) for n, v in shapes.items()), reverse=True)
                lighting_candidates[index] = lighting
        if unresolved:
            recognized = WindowsKoreanOcr().atomic_ocr_for_single_lines(
                [self.prepare_fallback(frames[i]) for i in unresolved])
            contrast_retry = []
            ambiguous_retry = []
            known_names = {entry['name'].get('kr') for entry in self.name_dictionary.values()}
            for index, result in zip(unresolved, recognized):
                value = ''.join(result)
                # Scroll header decoration can be read as a trailing quote.
                # Remove it only with independent strict-template agreement;
                # do not loosen the template ambiguity margin or guess Hangul.
                clean = value.strip(' \t\r\n『』「」')
                candidates = fallback_candidates[index]
                if (value in known_names and candidates and candidates[0][0] > 0.94
                        and value != candidates[0][1]):
                    # Two individually valid product names disagree: neither
                    # source is sufficient to authorize selecting a recipe.
                    values[index] = ''
                    continue
                if (clean != value and candidates and candidates[0][0] > 0.94
                        and (len(candidates) == 1 or candidates[1][0] < 0.94)
                        and clean == candidates[0][1]):
                    value = clean
                values[index] = value
                if value not in known_names:
                    shapes = shape_candidates[index]
                    if (shapes and shapes[0][1] in lighting_candidates[index]
                            and len(lighting_candidates[index]) == 1
                            and (len(shapes) == 1 or shapes[0][0] - shapes[1][0] > .10)
                            and (not candidates or candidates[0][0] <= .94)):
                        values[index] = shapes[0][1]
                        logger.info('KR whole-label bounded lighting agreement: %s' % shapes[0][1])
                        continue
                    from module.island_handler.korean_name_mask import mask_consensus
                    frame = frames[index]
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
                    masked = mask_consensus(gray, self.mask_references)
                    if masked:
                        values[index] = masked
                        logger.info('KR whole-label mask consensus: %s' % masked)
                        continue
                    shapes = shape_candidates[index]
                    if (shapes and shapes[0][0] > .96 and (not candidates or candidates[0][0] <= .94)
                            and (len(shapes) == 1 or shapes[0][0] - shapes[1][0] > .10)):
                        from module.island_handler.korean_name_mask import long_label_coverage_agrees
                        name = shapes[0][1]
                        if long_label_coverage_agrees(gray, self.mask_references, name):
                            values[index] = name
                            logger.info('KR long-label grayscale and ink coverage agree: %s' % name)
                            continue
                    if (shapes and shapes[0][0] > .97 and (not candidates or candidates[0][0] <= .94)
                            and (len(shapes) == 1 or shapes[0][0] - shapes[1][0] > .10)):
                        # A background-dependent exact reference is not itself
                        # authority. Require whole-label geometry above and
                        # three independent contrast OCR readings to agree.
                        name = shapes[0][1]
                        reads = WindowsKoreanOcr().atomic_ocr_for_single_lines([
                            self.prepare_fallback(np.where(gray < level, 0, 255).astype(np.uint8))
                            for level in (130, 150, 170)])
                        if (len(reads) == 3 and all(
                                ''.join(''.join(read).split()) == ''.join(name.split()) for read in reads)):
                            values[index] = name
                            logger.info('KR whole-label shape and triple OCR consensus: %s' % name)
                            continue
                if (value not in known_names and len(candidates) > 1
                        and candidates[0][0] > 0.94 and candidates[1][0] >= 0.94
                        and candidates[0][0] > candidates[1][0]):
                    ambiguous_retry.append(index)
                # Retry unknown OCR text once, but never replace another valid
                # product name. The second reading must exactly confirm the
                # independently strong image candidate.
                if (value not in known_names and candidates and candidates[0][0] > 0.94
                        and (len(candidates) == 1 or candidates[1][0] < 0.94)):
                    contrast_retry.append(index)
            if contrast_retry:
                contrast_frames = []
                for index in contrast_retry:
                    frame = frames[index]
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
                    ink = np.where(gray < 110, 0, 255).astype(np.uint8)
                    contrast_frames.append(self.prepare_fallback(ink))
                confirmed = WindowsKoreanOcr().atomic_ocr_for_single_lines(contrast_frames)
                localized_indices = []
                localized_frames = []
                for index, result in zip(contrast_retry, confirmed):
                    name = fallback_candidates[index][0][1]
                    value = ''.join(result)
                    if value == name:
                        values[index] = name
                    elif value not in known_names:
                        localized = self.localized_fallbacks(frames[index])
                        if len(localized) == 3:
                            localized_frames.extend(localized)
                            localized_indices.append(index)
                confirmed = WindowsKoreanOcr().atomic_ocr_for_single_lines(localized_frames) if localized_frames else []
                for i, index in enumerate(localized_indices):
                    name = fallback_candidates[index][0][1]
                    if len(confirmed) != 3 * len(localized_indices):
                        continue
                    votes = [''.join(value) for value in confirmed[3*i:3*i+3]]
                    if confirmed_contrast_name(name, votes, known_names):
                        values[index] = name
                    elif not any(value in known_names and value != name for value in votes):
                        # Bright translucent cards can put complete Hangul
                        # strokes above 130. Require independent high-level
                        # agreement too; never repair a valid-name conflict.
                        frame = frames[index]
                        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
                        bright = [self.prepare_fallback(np.where(gray < level, 0, 255).astype(np.uint8))
                                  for level in (150, 170, 190)]
                        bright_reads = WindowsKoreanOcr().atomic_ocr_for_single_lines(bright)
                        if confirmed_contrast_name(name, [''.join(value) for value in bright_reads], known_names):
                            values[index] = name
                            logger.info('KR recipe bright-context consensus: %s' % name)
            if ambiguous_retry:
                # Similar Hangul may have two high image scores. Do not
                # choose by that tiny margin alone: two of three ink levels
                # must read the exact candidate and no valid competing name
                # may be outvoted. Original valid-name conflicts stop above.
                retry_frames = []
                for index in ambiguous_retry:
                    frame = frames[index]
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
                    retry_frames.extend(self.prepare_fallback(np.where(gray < level, 0, 255).astype(np.uint8))
                                        for level in (90, 110, 130))
                reads = WindowsKoreanOcr().atomic_ocr_for_single_lines(retry_frames)
                for i, index in enumerate(ambiguous_retry):
                    name = fallback_candidates[index][0][1]
                    if len(reads) != 3 * len(ambiguous_retry):
                        continue
                    votes = [''.join(value) for value in reads[3*i:3*i+3]]
                    if confirmed_contrast_name(name, votes, known_names):
                        values[index] = name
                    elif not any(value in known_names and value != name for value in votes):
                        glyphs = self.glyph_fallbacks(frames[index])
                        if len(glyphs) == 3:
                            glyph_reads = WindowsKoreanOcr().atomic_ocr_for_single_lines(glyphs)
                            if confirmed_contrast_name(name, [''.join(value) for value in glyph_reads], known_names):
                                values[index] = name
                                logger.info('KR recipe glyph-context consensus: %s' % name)
        logger.attr(self.name or 'KR_ISLAND_NAMES', values)
        return values[0] if len(self.buttons) == 1 else values
