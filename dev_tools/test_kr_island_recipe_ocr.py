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
for filename, expected in [('2704_recipe_scroll_selected', '황광석'),
                           ('2605_recipe_background_selected', '양모'),
                           ('2010_recipe_selected', '아마'), ('2011_recipe_middle', '딸기'),
                           ('2012_recipe_middle', '목화'), ('2014_recipe_bottom', '찻잎')]:
    frame = np.array(Image.open('assets/kr/island_item_name/' + filename + '.png'))
    with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
        assert ocr.ocr([frame], direct_ocr=True) == [expected]
        backend.assert_not_called()
banana_selected = np.array(Image.open('assets/kr/island_item_name/2018_recipe_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([banana_selected], direct_ocr=True) == ['바나나']
    backend.assert_not_called()
sulfur_lower = np.array(Image.open('assets/kr/island_item_name/2704_recipe_lower_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([sulfur_lower], direct_ocr=True) == ['황광석']
    backend.assert_not_called()
sulfur_middle = np.array(Image.open('assets/kr/island_item_name/2704_recipe_middle_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([sulfur_middle], direct_ocr=True) == ['황광석']
    backend.assert_not_called()
apple_background = np.array(Image.open('dev_tools/fixtures/kr_apple_name_background.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([apple_background], direct_ocr=True) == ['사과']
    backend.assert_not_called()
pear = np.array(Image.open('assets/kr/island_item_name/4005_recipe_top.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([pear], direct_ocr=True) == ['아키즈키 배']
    backend.assert_not_called()
apple = np.array(Image.open('assets/kr/island_item_name/2016_recipe_up_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([apple], direct_ocr=True) == ['사과']
    backend.assert_not_called()
lemon_background = np.array(Image.open('dev_tools/fixtures/kr_lemon_name_background.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([lemon_background], direct_ocr=True) == ['레몬']
    backend.assert_not_called()
persimmon_variant = np.array(Image.open('assets/kr/island_item_name/4007_recipe_background_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([persimmon_variant], direct_ocr=True) == ['감']
    backend.assert_not_called()
persimmon = np.array(Image.open('assets/kr/island_item_name/4007_recipe_top_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([persimmon], direct_ocr=True) == ['감']
    backend.assert_not_called()
bright_sulfur = np.array(Image.open('dev_tools/fixtures/kr_sulfur_bright_name.png'))
for votes, expected in [([['황광석'], ['황광석'], ['황광석']], '황광석'),
                        ([[], ['황광석'], ['황광석']], '황광식'),
                        ([['철광석'], ['황광석'], ['황광석']], '황광식'),
                        ([['황광석']], '황광식'), ([[], [], []], '황광식')]:
    with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
        backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['황광식']], [[], [], []], votes]
        assert ocr.ocr([bright_sulfur], direct_ocr=True) == [expected]
        assert backend.return_value.atomic_ocr_for_single_lines.call_count == 3
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['황광식']], [[], ['철광석'], []]]
    assert ocr.ocr([bright_sulfur], direct_ocr=True) == ['황광식']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 2
component_tuna = np.array(Image.open('dev_tools/fixtures/kr_tuna_components_name.png'))
for votes, expected in [([[], ['참치'], ['참치']], '참치'),
                        ([['삼치'], ['참치'], ['참치']], '참자'),
                        ([['참치']], '참자'), ([[], [], []], '참자')]:
    with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
        backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['참자']], [[], [], []], votes]
        assert ocr.ocr([component_tuna], direct_ocr=True) == [expected]
        assert backend.return_value.atomic_ocr_for_single_lines.call_count == 3
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['참자']], [[], ['삼치'], []]]
    assert ocr.ocr([component_tuna], direct_ocr=True) == ['참자']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 2
assert ocr.glyph_fallbacks(np.full((31,146,3),255,dtype=np.uint8)) == []
decoration = np.full((31,146,3),255,dtype=np.uint8)
decoration[20:22,10:130] = 0
assert ocr.glyph_fallbacks(decoration) == []
iron_up = np.array(Image.open('assets/kr/island_item_name/2703_recipe_up_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([iron_up], direct_ocr=True) == ['철광석']
    backend.assert_not_called()
lemon = np.array(Image.open('dev_tools/fixtures/kr_lemon_name_context.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([lemon], direct_ocr=True) == ['레몬']
    backend.assert_not_called()
sulfur = np.array(Image.open('dev_tools/fixtures/kr_sulfur_name_context.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['황광석']]
    assert ocr.ocr([sulfur], direct_ocr=True) == ['황광석']
    backend.assert_called_once()
localized_mackerel = np.array(Image.open('dev_tools/fixtures/kr_mackerel_localized_name.png'))
for reads, expected in [([['삼치']] * 3, '삼치'),
                        ([['삼치'], ['참치'], ['삼치']], '삼자1'),
                        ([['삼치']], '삼자1')]:
    with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
        backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['삼자1']], [['삼시']], reads]
        assert ocr.ocr([localized_mackerel], direct_ocr=True) == [expected]
        assert backend.return_value.atomic_ocr_for_single_lines.call_count == 3
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['삼자1']], [['참치']]]
    assert ocr.ocr([localized_mackerel], direct_ocr=True) == ['삼자1']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 2
assert ocr.localized_fallbacks(np.full((23, 146, 3), 255, dtype=np.uint8)) == []
decorated_mackerel = np.array(Image.open('assets/kr/island_item_name/5102_recipe_decoration_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([decorated_mackerel], direct_ocr=True) == ['삼치']
    backend.assert_not_called()
wool = np.array(Image.open('assets/kr/island_item_name/2605_recipe_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([wool], direct_ocr=True) == ['양모']
    backend.assert_not_called()
iron_offset = np.array(Image.open('assets/kr/island_item_name/2703_recipe_offset_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([iron_offset], direct_ocr=True) == ['철광석']
    backend.assert_not_called()
dot_tuna = np.array(Image.open('dev_tools/fixtures/kr_tuna_dot_name.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[[]], [['참치'], ['참치'], ['참치']]]
    assert ocr.ocr([dot_tuna], direct_ocr=True) == ['참치']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 2
mining_top = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_top.png' % i)) for i in [2700,2701]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr(mining_top, direct_ocr=True) == ['석탄', '구리 광석']
    backend.assert_not_called()
ambiguous_tuna = np.array(Image.open('dev_tools/fixtures/kr_tuna_ambiguous_name.png'))
for reads, expected in [([['참치'], ['참치'], ['참치']], '참치'),
                        ([['참치'], ['삼치'], ['참치']], '미인식'),
                        ([[], [], ['참치']], '미인식'),
                        ([['삼치'], ['삼치'], ['삼치']], '미인식')]:
    with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
        backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['미인식']], reads, [[], [], []]]
        assert ocr.ocr([ambiguous_tuna], direct_ocr=True) == [expected]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['삼치']]
    assert ocr.ocr([ambiguous_tuna], direct_ocr=True) == ['']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 1
selected_tuna = np.array(Image.open('assets/kr/island_item_name/5103_recipe_selected.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([selected_tuna], direct_ocr=True) == ['참치']
    backend.assert_not_called()
mackerel = np.array(Image.open('dev_tools/fixtures/kr_mackerel_name.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['삼지']], [['삼치']]]
    assert ocr.ocr([mackerel], direct_ocr=True) == ['삼치']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 2
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[['삼지']], [['참치']]]
    assert ocr.ocr([mackerel], direct_ocr=True) == ['삼지']
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['참치']]
    assert ocr.ocr([mackerel], direct_ocr=True) == ['']
    assert backend.return_value.atomic_ocr_for_single_lines.call_count == 1
salmon = np.array(Image.open('assets/kr/island_item_name/5104_recipe_top.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([salmon], direct_ocr=True) == ['연어']
    backend.assert_not_called()
header = np.array(Image.open('assets/kr/island_item_name/2000_header.png'))
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr([header], direct_ocr=True) == ['밀']
    backend.assert_not_called()
bottom_fish = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_bottom.png' % i))
               for i in [5105, 5106, 5107, 5108]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr(bottom_fish, direct_ocr=True) == ['참돔', '감성돔', '황다랑어', '해삼']
    backend.assert_not_called()
up_fish = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_up.png' % i))
           for i in [5103, 5104, 5105, 5106]]
with patch.object(ocr, 'pixel_exact_match', return_value=False), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['참치』']]
    assert ocr.ocr(up_fish, direct_ocr=True) == ['참치', '연어', '참돔', '감성돔']
    backend.assert_called_once()
with patch.object(ocr, 'pixel_exact_match', return_value=False), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['삼치』']]
    assert ocr.ocr(up_fish[:1], direct_ocr=True) == ['삼치』']
with patch.object(ocr, 'pixel_exact_match', return_value=False), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['참똲』']]
    assert ocr.ocr(up_fish[:1], direct_ocr=True) == ['참똲』']
ids = [2000, 2001, 2008, 2009]
mining = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_bottom.png' % i))
          for i in [2702, 2703, 2704, 2705]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    assert ocr.ocr(mining, direct_ocr=True) == ['알루미늄 광석', '철광석', '황광석', '은광석']
    backend.assert_not_called()
middle_fish = [np.array(Image.open('assets/kr/island_item_name/%s_recipe_middle.png' % i))
               for i in [5101, 5102]]
with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.return_value = [['삼치']]
    assert ocr.ocr(middle_fish, direct_ocr=True) == ['오징어', '삼치']
from pathlib import Path
observed_ids = {int(p.stem.split('_')[0]) for p in Path(ocr.template_folder).glob('*.png')}
assert set(range(5001, 5009)) | set(range(5101, 5109)) <= observed_ids
with patch.object(ocr, 'pixel_exact_match', return_value=False), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[[]], [['삼치']]]
    assert ocr.ocr(middle_fish[1:], direct_ocr=True) == ['삼치']
with patch.object(ocr, 'pixel_exact_match', return_value=False), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
    backend.return_value.atomic_ocr_for_single_lines.side_effect = [[[]], [['참치']]]
    assert ocr.ocr(middle_fish[1:], direct_ocr=True) == ['']
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
