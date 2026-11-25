"""Read-only local name crop diagnostics, no game input."""
from types import SimpleNamespace
from PIL import Image
import numpy as np
import module.config.server as server
server.server = 'kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe

if __name__ == '__main__':
    import sys
    im = np.array(Image.open(sys.argv[1]).convert('RGB'))
    ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
    ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
    grid = IslandRecipe.get_recipe_grid(ui)
    for i, button in enumerate(grid.crop((123,19,269,50)).buttons):
        print(i, button.area)
        Image.fromarray(crop(im,button.area)).save('log/kr_name_probe_%s.png' % i)
