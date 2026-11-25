"""Reviewed public labels only; reject overwritten source frames."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from PIL import Image
import numpy as np
import module.config.server as server
server.server='kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe

ROWS = [
 ('501_9101',0,4007,'c261d5e532edd4c08f4eccf0c650a2d1b6fa07f108e23d38b460fc3d411d3ba6'),
 ('601_9061',1,3014,'f94e54e43657ea54bf8d49612145380d3fbd2d9da399d82d53439b6d81b25e82'),
 ('602_9071',1,3104,'b32798357cbc5c736c2c25165f717b4019df8ac87168a91b0b6d87707a6cdbb4'),
 ('603_9081',2,3108,'40a989eef8809a3b7cef5eb0d840dfa383254b4c4884e250e821b0a93fa9935e'),
 ('604_9091',1,3033,'2cd570351a2b454b4b1ecba27f3ed0e2d5acf4f4afd7134107f1d06887dd8023'),
 ('604_9091',2,3034,'2cd570351a2b454b4b1ecba27f3ed0e2d5acf4f4afd7134107f1d06887dd8023'),
 ('703_9201',0,3049,'a6fccd9210bdb90a0ef932b4d0d88f91d5aabab224b284be56354b17ba5746a8'),
 ('704_9203',0,3044,'20e02805ea42d95105ad0c9813daf2c7ac9062d3bf480d92d766d419255f4354'),
 ('706_9207',0,3035,'f72d130eef88e8314e7214791e305af4293dfecd25452c10eae174479ca2fc8d'),
 ('901_9041',1,3010,'6d971b62ebd4c68636326f3679dabdd75c762d619c7d84ca08a9a245e0847b2a'),
]
if __name__ == '__main__':
    # Fixtures first. References are copied from these reviewed fixtures only
    # after the failing regression, so later live frames cannot relabel them.
    for key,row,item,digest in ROWS:
        path=Path('log/kr_recipe_review_0916/kr_island_recipe_audit_%s.png'%key)
        if sha256(path.read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Source frame changed; review again: %s'%path)
        im=np.array(Image.open(str(path)).convert('RGB'))
        ui=SimpleNamespace(image_crop=lambda area,copy=True:crop(im,area,copy=copy))
        ui._get_recipe_buttons=lambda:IslandRecipe._get_recipe_buttons(ui)
        grid=IslandRecipe.get_recipe_grid(ui)
        Image.fromarray(crop(im,grid.crop((123,19,269,50)).buttons[row].area)).save(
            'dev_tools/fixtures/kr_scroll_phase_%s.png'%item)
