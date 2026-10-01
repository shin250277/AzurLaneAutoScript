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
        return frame

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
        for index, frame in enumerate(frames):
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            scores = {}
            for name, template in self.templates:
                if gray.shape[0] >= template.shape[0] and gray.shape[1] >= template.shape[1]:
                    score = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))[1]
                    if np.isfinite(score):
                        scores[name] = max(score, scores.get(name, 0))
            # Multiple observed scroll renderings of the same name are not
            # competing identities; ambiguity is between different products.
            candidates = sorted(((score, name) for name, score in scores.items()), reverse=True)
            if candidates and candidates[0][0] > 0.94 and (len(candidates) == 1 or candidates[0][0] - candidates[1][0] > 0.10):
                values.append(candidates[0][1])
            else:
                values.append('')
                unresolved.append(index)
        if unresolved:
            recognized = WindowsKoreanOcr().atomic_ocr_for_single_lines(
                [self.prepare_fallback(frames[i]) for i in unresolved])
            for index, result in zip(unresolved, recognized):
                values[index] = ''.join(result)
        logger.attr(self.name or 'KR_ISLAND_NAMES', values)
        return values[0] if len(self.buttons) == 1 else values
