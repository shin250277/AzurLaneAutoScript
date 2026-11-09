"""Read-only local failure-frame replay with actual KR OCR; no device input."""
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
import numpy as np
import module.config.server as server
server.server = 'kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe, recipe_product_name_to_recipe_id
from module.island_handler.korean_ocr import KoreanIslandNameOcr


if __name__ == '__main__':
    failures = []
    for path in sorted(Path('log').glob('kr_island_recipe_audit_*.png')):
        im = np.array(Image.open(str(path)).convert('RGB'))
        ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
        ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
        grid = IslandRecipe.get_recipe_grid(ui)
        frames = [crop(im, button.area) for button in grid.crop((123, 19, 269, 50)).buttons]
        names = KoreanIslandNameOcr([]).ocr(frames, direct_ocr=True)
        slot = int(path.stem.split('_')[-1])
        ids = [recipe_product_name_to_recipe_id(name, slotcode=slot) for name in names]
        if not ids or any(not identity for identity in ids) or len(set(ids)) != len(ids):
            failures.append((path.name, names))
        print(path.stem, names, ids)
    if failures:
        raise AssertionError('Unknown/ambiguous recipes: %r' % failures)
