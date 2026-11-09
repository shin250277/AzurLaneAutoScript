"""Replay the full KR identity path on local recipe screenshots, no devices."""
from pathlib import Path
from types import SimpleNamespace
import sys
from module.base.utils import crop, load_image
import module.config.server as server
server.server = 'kr'
from module.island_handler.recipe import IslandRecipe


class OfflineDevice:
    def sleep(self, seconds):
        pass

    def screenshot(self):
        pass

    def image_save(self, path):
        pass


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        path = Path(filename)
        im = load_image(str(path))
        ui = SimpleNamespace(image_crop=lambda area,copy=True:crop(im,area,copy=copy),
                             working_slot_id=int(path.stem.split('_')[-1]),
                             device=OfflineDevice(), is_in_recipe_menu=lambda:True)
        ui._get_recipe_buttons = lambda:IslandRecipe._get_recipe_buttons(ui)
        ui.get_recipe_grid = lambda:IslandRecipe.get_recipe_grid(ui)
        ui.recipe_grid = ui.get_recipe_grid()
        result = IslandRecipe.get_recipe_ids(ui)
        if not result or None in result or len(set(result)) != len(result):
            raise AssertionError('Incomplete or duplicated identity')
        print(path.name, result, flush=True)
