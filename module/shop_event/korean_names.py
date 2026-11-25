"""Strict public Korean shop-label matching, independent of similar icons."""
from pathlib import Path
import cv2
import numpy as np
from module.base.utils import load_image


class KoreanShopNames:
    def __init__(self):
        self.templates = []
        for path in Path('assets/shop/event_kr_names').glob('*.png'):
            gray = cv2.cvtColor(load_image(str(path)), cv2.COLOR_RGB2GRAY)
            y, x = np.where(gray < 110)
            if not len(x):
                continue
            template = cv2.GaussianBlur(gray, (3, 3), 0)[
                max(0, y.min()-1):min(gray.shape[0], y.max()+2),
                max(0, x.min()-1):min(gray.shape[1], x.max()+2)]
            self.templates.append((path.stem.split('__', 1)[0], template))

    def match(self, frame):
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (3, 3), 0)
        candidates = {}
        for name, template in self.templates:
            if gray.shape[0] < template.shape[0] or gray.shape[1] < template.shape[1]:
                continue
            score = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))[1]
            if np.isfinite(score):
                candidates[name] = max(score, candidates.get(name, 0))
        scores = sorted(((score, name) for name, score in candidates.items()), reverse=True)
        if scores and scores[0][0] >= 0.94 and (len(scores) == 1 or scores[0][0]-scores[1][0] >= 0.04):
            return scores[0][1]
        return None
