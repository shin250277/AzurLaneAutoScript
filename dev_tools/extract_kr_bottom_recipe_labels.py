"""Public names only, reviewed Nov 9 08:53-56 frames, actual detected grid."""
from types import SimpleNamespace
from PIL import Image
import numpy as np
import module.config.server as server
server.server = 'kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe

LABELS = [('601_9061',1,3114), ('602_9071',1,3103), ('602_9071',2,3104),
          ('603_9081',1,3009), ('604_9091',1,3033), ('604_9091',2,3034),
          ('703_9201',2,3117), ('704_9203',0,3044), ('704_9203',2,3046),
          ('706_9207',2,3037), ('901_9041',1,3010)]

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--reference', action='store_true')
    args = p.parse_args()
    for key, row, item in LABELS:
        if args.reference and item == 3103:
            continue  # Full faint-stroke extent fixes this using existing references.
        im = np.array(Image.open('log/kr_island_recipe_audit_%s.png' % key).convert('RGB'))
        ui = SimpleNamespace(image_crop=lambda area,copy=True:crop(im,area,copy=copy))
        ui._get_recipe_buttons = lambda:IslandRecipe._get_recipe_buttons(ui)
        grid = IslandRecipe.get_recipe_grid(ui)
        area = grid.crop((123,19,269,50)).buttons[row].area
        target = ('assets/kr/island_item_name/%s_bottom_full_selected.png' % item if args.reference
                  else 'dev_tools/fixtures/kr_bottom_full_%s.png' % item)
        Image.fromarray(crop(im,area)).save(target)
