"""Read-only local label/template brightness diagnostics."""
from types import SimpleNamespace
from PIL import Image
import numpy as np
import cv2
import module.config.server as server
server.server = 'kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe
from module.island_handler.korean_ocr import KoreanIslandNameOcr

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('frame')
    p.add_argument('row', type=int)
    args = p.parse_args()
    im = np.array(Image.open(args.frame).convert('RGB'))
    ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
    ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
    grid = IslandRecipe.get_recipe_grid(ui)
    frame = cv2.cvtColor(crop(im, grid.crop((123, 19, 269, 50)).buttons[args.row].area), cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(frame, (5, 5), 0)
    scores = []
    for name, template, exact in KoreanIslandNameOcr([]).templates:
        if gray.shape[0] < template.shape[0] or gray.shape[1] < template.shape[1]:
            continue
        _, value, _, point = cv2.minMaxLoc(cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED))
        if not KoreanIslandNameOcr.complete_label_span(frame, point[0], point[0]+template.shape[1]):
            continue
        observed = gray[point[1]:point[1]+template.shape[0], point[0]:point[0]+template.shape[1]]
        delta = observed.astype(float)-template.astype(float)
        offset = np.median(delta)
        x, y = template.astype(float), observed.astype(float)
        gain = ((x-x.mean())*(y-y.mean())).sum()/((x-x.mean())**2).sum()
        shift = y.mean()-gain*x.mean()
        residual = np.abs(y-(gain*x+shift))
        scores.append((value, name, exact, float(np.abs(delta).mean()), float(offset), float(np.abs(delta-offset).mean()),
                       float(gain), float(shift), float(residual.mean()), float(np.percentile(residual,99))))
    print(sorted(scores, reverse=True)[:8])
