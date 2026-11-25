"""Reviewed tiny labels/icons/numerals only; no account or full-screen export."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from module.base.utils import crop, load_image
import module.config.server as server
server.server = 'kr'
from module.island_handler.recipe import IslandRecipe


def grid(path):
    im = load_image(str(path))
    ui = SimpleNamespace(image_crop=lambda area, copy=True: crop(im, area, copy=copy))
    ui._get_recipe_buttons = lambda: IslandRecipe._get_recipe_buttons(ui)
    return im, IslandRecipe.get_recipe_grid(ui)


if __name__ == '__main__':
    for filename, digest, area, row, output in [
        ('kr_island_stock_previous.png', 'aecd86ab7786eccccd516fa4667a8175b3b9dc21ab94f958ce804f7ec60bd3ee',
         (212,92,275,114), 2, 'kr_stock_61_previous.png'),
        ('kr_island_stock_unknown.png', '6a76cd4c1943cd05bffeaa074996441fdc370e9404619cf4f5ad47674df9a504',
         (212,92,275,114), 0, 'kr_stock_61_followup.png'),
        ('kr_island_recipe_audit_601_9061.png', '2f8f2380e86fe3f2740b5ba62ae431aa38fc92cdf25ca648894acc7e9cbe1d72',
         (123,19,269,50), 2, 'kr_fish_chips_followup.png'),
        ('kr_island_recipe_audit_602_9071.png', '9d039712b2091ef272df34b5a08585f8d60b3281d5e7d959c39747387e12e7e1',
         (20,20,115,115), 2, 'kr_fruit_paradise_icon.png'),
    ]:
        path = Path('log') / filename
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires review')
        im, buttons = grid(path)
        Image.fromarray(crop(im, buttons.crop(area).buttons[row].area)).save('dev_tools/fixtures/' + output)
    target = Path('assets/kr/island_recipe_icon')
    target.mkdir(parents=True, exist_ok=True)
    # Exclude quantity and border; only public fruit artwork remains.
    Image.open('dev_tools/fixtures/kr_fruit_paradise_icon.png').crop((8,8,84,76)).save(str(target / '3104.png'))
