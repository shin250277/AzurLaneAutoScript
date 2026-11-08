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
    def pixel_exact_match(candidates, errors):
        """Require near-identical observed pixels, not just shape correlation."""
        return bool(candidates and candidates[0][0] > 0.995
                    and errors[candidates[0][1]] < 1.0
                    and all(errors[name] > 5.0 for _, name in candidates[1:]))

    @cached_property
    def templates(self):
        templates = []
        for path in Path(self.template_folder).glob('*.png'):
            gray = cv2.cvtColor(load_image(str(path)), cv2.COLOR_RGB2GRAY)
            y, x = np.where(gray < 110)
            if not len(x):
                continue
            # Ignore the translucent card background, which changes as the
            # list scrolls across scenery. Retain a small margin around ink.
            template = cv2.GaussianBlur(gray, (5, 5), 0)[
                max(int(y.min())-1, 0):min(int(y.max())+2, gray.shape[0]),
                max(int(x.min())-2, 0):min(int(x.max())+3, gray.shape[1])]
            templates.append((self.name_dictionary[int(path.stem.split('_')[0])]['name']['kr'],
                              template, path.stem.endswith('_selected')))
        return templates

    def ocr(self, image, direct_ocr=False):
        frames = image if direct_ocr else [crop(image, area) for area in self.buttons]
        values = []
        unresolved = []
        fallback_candidates = {}
        for index, frame in enumerate(frames):
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            scores = {}
            spans = {}
            errors = {}
            for name, template, exact_only in self.templates:
                if gray.shape[0] >= template.shape[0] and gray.shape[1] >= template.shape[1]:
                    _, score, _, point = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))
                    observed = gray[point[1]:point[1] + template.shape[0],
                                    point[0]:point[0] + template.shape[1]]
                    error = float(np.abs(observed.astype(np.float32) - template).mean())
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
