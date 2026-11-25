"""Reviewed public icons/labels only, excluding stock counters and account UI."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from PIL import Image
from module.base.utils import crop, load_image
import module.config.server as server
server.server = 'kr'
from module.island_handler.recipe import IslandRecipe

if __name__ == '__main__':
    sources = {'601_9061':'5e6c37c14c4872feef9628e020fbd1e8caad92beecc8bef939fc84e0e1e0eff9',
               '604_9091':'af985babaebb52560e2e4d4a6d80732e17a2258d13e442323e0810210991d51e'}
    for key,digest in sources.items():
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Source changed; review again before extracting')
        im = load_image(str(path))
        ui = SimpleNamespace(image_crop=lambda area,copy=True:crop(im,area,copy=copy))
        ui._get_recipe_buttons = lambda:IslandRecipe._get_recipe_buttons(ui)
        grid = IslandRecipe.get_recipe_grid(ui)
        for row in range(3):
            for kind, area in [('icon',(20,20,115,115)), ('name',(123,19,269,50))]:
                frame = crop(im,grid.crop(area).buttons[row].area)
                Image.fromarray(frame).save('dev_tools/fixtures/kr_recipe_%s_%s_%s.png' % (key,row,kind))
