"""Only exact, unambiguous Korean product names may select recipes."""
import subprocess
import sys
import unittest


class KoreanRecipeOcrTest(unittest.TestCase):
    def test_observed_names_and_reject_unknown(self):
        code = '''
import numpy as np
from unittest.mock import patch
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.recipe import recipe_product_name_to_recipe_id
from module.island.data import DIC_ISLAND_ITEM
ocr = KoreanIslandNameOcr([])
header = np.array(Image.open('assets/kr/island_item_name/2000_header.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([header], direct_ocr=True) == ['밀']
    backend.assert_not_called()
ids = [2000, 2001, 2008, 2009]
frames = [np.array(Image.open('assets/kr/island_item_name/%s.png' % i)) for i in ids]
assert ocr.ocr(frames, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in ids]
egg = np.array(Image.open('assets/kr/island_item_name/2601_recipe.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([egg], direct_ocr=True) == ['달걀']
    backend.assert_not_called()
fish = [np.array(Image.open('assets/kr/island_item_name/%s_recipe.png' % i))
        for i in [5001, 5002, 5003, 5004]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr(fish, direct_ocr=True) == ['조개', '메기', '잉어', '붕어']
    backend.assert_not_called()
lower = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_lower.png' % i))
         for i in [5005, 5006, 5007, 5008]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr(lower, direct_ocr=True) == ['민물 새우', '가재', '농어', '게']
    backend.assert_not_called()
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
    assert ocr.ocr([np.zeros((23,146,3),dtype=np.uint8)], direct_ocr=True) == ['']
assert recipe_product_name_to_recipe_id('') is None
assert recipe_product_name_to_recipe_id('not a product') is None
assert recipe_product_name_to_recipe_id(DIC_ISLAND_ITEM[2000]['name']['kr']) is not None
frame = np.array(Image.open('dev_tools/fixtures/kr_island_recipe_scrolled.png'))
rows = [frame[y:y+23,304:450] for y in [145,294,443,592]]
assert ocr.ocr(rows, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in [2008,2009,2002,2003]]
frame = np.array(Image.open('dev_tools/fixtures/kr_island_recipe_scrolled_second.png'))
rows = [frame[y:y+23,304:450] for y in [197,346,495]]
assert ocr.ocr(rows, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in [2002,2003,2005]]
frame = np.array(Image.open('dev_tools/fixtures/kr_island_recipe_bottom.png'))
rows = [frame[y:y+23,304:450] for y in [94,243,392,541]]
assert ocr.ocr(rows, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in [2002,2003,2005,2006]]
frame = np.array(Image.open('dev_tools/fixtures/kr_island_recipe_up.png'))
rows = [frame[y:y+23,304:450] for y in [80,229,378,527]]
assert ocr.ocr(rows, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in [2000,2001,2008,2009]]
frame = np.array(Image.open('dev_tools/fixtures/kr_island_recipe_up_middle.png'))
rows = [frame[y:y+23,304:450] for y in [93,242,391,540]]
assert ocr.ocr(rows, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in [2008,2009,2002,2003]]
'''
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
