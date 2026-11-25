"""Recognize observed, non-premium KR event tokens before enabling purchases.

Unknown event tokens, UR exchange currency and diamonds are NOT inferred from
price or from being on an event tab. New artwork requires a reviewed reference.
"""
from pathlib import Path
import cv2
import numpy as np
from module.base.utils import load_image


class KoreanEventCurrency:
    def __init__(self):
        self.references = [(path.stem, load_image(str(path)))
                           for path in sorted(Path('assets/shop/event_kr_currency').glob('*.png'))]

    def identify(self, image):
        if not isinstance(image, np.ndarray) or image.ndim != 3 or np.std(image) < 10:
            return None
        scores = {}
        for name, template in self.references:
            if image.shape[0] < template.shape[0] or image.shape[1] < template.shape[1]:
                continue
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, score, _, point = cv2.minMaxLoc(result)
            if not np.isfinite(score):
                continue
            observed = image[point[1]:point[1]+template.shape[0], point[0]:point[0]+template.shape[1]]
            error = np.abs(observed.astype(float)-template.astype(float)).mean()
            if score >= .96 and error <= 18:
                identity = name.split('__', 1)[0]
                scores[identity] = max(score, scores.get(identity, 0))
        scores = sorted(((v, k) for k, v in scores.items()), reverse=True)
        if scores and (len(scores) == 1 or scores[0][0]-scores[1][0] >= .05):
            return scores[0][1]
        return None


def validated_point_items(items, token):
    return bool(items and token in ('train_pt', 'skull_pt', 'guitar_pt') and all(
        getattr(item, 'kr_currency_token', None) == token
        and getattr(item, 'cost', None) == 'pt'
        and type(getattr(item, 'price', None)) is int and item.price > 0
        and type(getattr(item, 'amount', None)) is int and item.amount > 0
        and type(getattr(item, 'count', None)) is int and item.count >= 0
        and type(getattr(item, 'total_count', None)) is int
        and 0 <= item.count <= item.total_count and item.total_count > 0
        for item in items))
