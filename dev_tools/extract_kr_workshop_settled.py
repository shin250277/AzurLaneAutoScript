"""Extract three reviewed public workshop labels, no stock/account data."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from PIL import Image
from module.base.utils import load_image, crop
import module.config.server as server
server.server = 'kr'
from module.island_handler.recipe import IslandRecipe

if __name__ == '__main__':
    for key, rows, digest in [
        ('703_9201', [(0, 3049)], 'aae7fb712138ddffd91b19df149b5f5a2fc23720526406cc8611eef37e2e3aa4'),
        ('704_9203', [(0, 3043), (1, 3044)], '35a75f6e66cf736bdacee9e7927f37a4f3eebafdfaa422cd0880bceb89867a7d'),
    ]:
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Source changed; review required')
        im = load_image(str(path))
        ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
        ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
        grid = IslandRecipe.get_recipe_grid(ui).crop((123, 19, 269, 50))
        for row, item in rows:
            Image.fromarray(crop(im, grid.buttons[row].area)).save('dev_tools/fixtures/kr_workshop_settled_%s.png' % item)
