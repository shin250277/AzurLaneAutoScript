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


class KoreanIslandNameOcr(Ocr):
    template_folder = 'assets/kr/island_item_name'
    name_dictionary = DIC_ISLAND_ITEM

    def prepare_fallback(self, frame):
        # Windows OCR can miss Hangul touching the right/bottom crop edge.
        # Keep all observed pixels and add context, rather than altering text.
        padding = ((20, 20), (20, 20)) + ((0, 0),) * (frame.ndim - 2)
        return np.pad(frame, padding, mode='constant', constant_values=255)

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
            templates.append((self.name_dictionary[int(path.stem.split('_')[0])]['name']['kr'], template))
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
            for name, template in self.templates:
                if gray.shape[0] >= template.shape[0] and gray.shape[1] >= template.shape[1]:
                    _, score, _, point = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))
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
            known_names = {entry['name'].get('kr') for entry in self.name_dictionary.values()}
            for index, result in zip(unresolved, recognized):
                value = ''.join(result)
                # Scroll header decoration can be read as a trailing quote.
                # Remove it only with independent strict-template agreement;
                # do not loosen the template ambiguity margin or guess Hangul.
                clean = value.strip(' \t\r\n『』「」')
                candidates = fallback_candidates[index]
                strong_candidate = bool(candidates and candidates[0][0] > 0.94
                                        and (len(candidates) == 1 or candidates[1][0] < 0.94))
                if value in known_names and strong_candidate and value != candidates[0][1]:
                    # Two individually valid product names disagree: neither
                    # source is sufficient to authorize selecting a recipe.
                    values[index] = ''
                    continue
                if (clean != value and candidates and candidates[0][0] > 0.94
                        and (len(candidates) == 1 or candidates[1][0] < 0.94)
                        and clean == candidates[0][1]):
                    value = clean
                values[index] = value
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
                for index, result in zip(contrast_retry, confirmed):
                    name = fallback_candidates[index][0][1]
                    if ''.join(result) == name:
                        values[index] = name
        logger.attr(self.name or 'KR_ISLAND_NAMES', values)
        return values[0] if len(self.buttons) == 1 else values
