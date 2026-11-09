"""Cross-check clipped KR recipe labels against the existing shared food icons.

No icon-only authorization and no guessed Hangul substitutions. This helper is
independent of spending; callers must still validate recipe/stock/cost evidence.
"""
from pathlib import Path
import re
import cv2
import numpy as np
from module.base.decorator import cached_property
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM, DIC_ISLAND_RECIPE, DIC_ISLAND_SLOT


def hangul(value):
    return ''.join(re.findall('[가-힣]', value))


def label_supports_icon(candidate, observed, known_names):
    expected, text = hangul(candidate), hangul(observed)
    if not text or len(expected) < 5:
        return False
    if any(hangul(name) == text and hangul(name) != expected for name in known_names):
        return False
    # Require at least four consecutive actually-read syllables, covering at
    # least half the full name. A generic short word like chicken cannot vote.
    return any(expected[i:i+size] in text
               for size in range(max(4, (len(expected)+1)//2), len(expected)+1)
               for i in range(len(expected)-size+1))


class KoreanRecipeIconVerifier:
    @cached_property
    def references(self):
        by_name = {v['name']['en'].replace(' ', '_'): key for key,v in DIC_ISLAND_ITEM.items()}
        refs = []
        for path in Path('assets/island/restaurant').glob('*.png'):
            if path.stem not in by_name:
                continue
            icon = load_image(str(path))[21:67,12:72]
            # Fixed UI geometry: recipe icons are larger than restaurant icons.
            for scale in (1.3, 1.325, 1.35, 1.375):
                refs.append((by_name[path.stem], cv2.resize(icon, None, fx=scale, fy=scale,
                                                         interpolation=cv2.INTER_CUBIC)))
        return refs

    def confirm(self, frame, observed_name, allowed_products):
        if not isinstance(frame, np.ndarray) or frame.shape != (95, 95, 3) or np.std(frame) < 10:
            return None
        scores = {}
        for item, ref in self.references:
            score = cv2.minMaxLoc(cv2.matchTemplate(frame, ref, cv2.TM_CCOEFF_NORMED))[1]
            if np.isfinite(score):
                scores[item] = max(score, scores.get(item, -1))
        ranked = sorted(((score,item) for item,score in scores.items()), reverse=True)
        if (not ranked or ranked[0][0] <= .90 or len(ranked) < 2
                or ranked[0][0]-ranked[1][0] <= .18):
            return None
        item = ranked[0][1]
        if item not in allowed_products:
            return None
        name = DIC_ISLAND_ITEM[item]['name']['kr']
        if not label_supports_icon(name, observed_name,
                                   [v['name'].get('kr','') for v in DIC_ISLAND_ITEM.values()]):
            return None
        return item


_VERIFIER = KoreanRecipeIconVerifier()


def resolve_recipe_icons(names, recipe_ids, frames, slot_id):
    """Fill unknown identities only, within this observed facility's formulas."""
    result = list(recipe_ids)
    if slot_id not in DIC_ISLAND_SLOT or not (len(names) == len(result) == len(frames)):
        return result
    slot = DIC_ISLAND_SLOT[slot_id]
    products = {}
    for recipe in slot['formula'] + slot['activity_formula']:
        for product in DIC_ISLAND_RECIPE[recipe]['commission_product']:
            products.setdefault(product, []).append(recipe)
    for index, (name, recipe, frame) in enumerate(zip(names, result, frames)):
        if recipe is not None:
            continue
        product = _VERIFIER.confirm(frame, name, products)
        if product is not None and len(products[product]) == 1:
            result[index] = products[product][0]
    return result
