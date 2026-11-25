"""Reviewed public names only from four local failure frames."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from PIL import Image
from module.base.utils import load_image, crop
import module.config.server as server
server.server = 'kr'
from module.island_handler.recipe import IslandRecipe

SOURCES = [
    ('402_9021', (2800, 2801, 2802), '509cb8bd4b3a0ef491bdee6cf3e7399ae256d27d07c5d9f52860d50fe46ed9f1'),
    ('602_9071', (3019, 3020, 3021), 'e699b29a0e8df8a5223589085f85a46d1c3e2f7fa63142288d2b4c52c3ca81f7'),
    ('603_9081', (3024, 3025, 3026), 'd326f377fbd2b5b93dabae2ceeb921e5786942b944374d6917634ef081a8d3b5'),
    ('901_9041', (3111, 3112, 3113), '51d5ae81d7226103891a5b1c2949a249c68a2418b3697e3d8d264f681ec61c3b'),
]

if __name__ == '__main__':
    for key, items, digest in SOURCES:
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Source changed; review required')
        im = load_image(str(path))
        ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
        ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
        grid = IslandRecipe.get_recipe_grid(ui).crop((123, 19, 269, 50))
        if len(grid.buttons) != len(items):
            raise RuntimeError('Unexpected row count')
        for item, button in zip(items, grid.buttons):
            Image.fromarray(crop(im, button.area)).save('dev_tools/fixtures/kr_settled_name_%s.png' % item)
