"""Korean order requirements must reject uncertain item identities."""
import subprocess
import sys
import unittest


class KoreanOrderOcrTest(unittest.TestCase):
    def test_observed_order_names_without_os_fallback(self):
        code = '''
from unittest.mock import patch
from module.island.korean_order_ocr import KoreanOrderNameOcr
from module.island.data import DIC_ISLAND_ITEM
from module.base.utils import load_image
ids = [2008, 2601, 3029, 2703, 2600]
frames = [load_image('assets/kr/island_item_name/%s_order.png' % i) for i in ids]
with patch('module.ocr.windows_ocr.WindowsKoreanOcr.atomic_ocr_for_single_lines',
           side_effect=AssertionError('Observed names should not need OS fallback')):
    assert KoreanOrderNameOcr([]).ocr(frames, direct_ocr=True) == [DIC_ISLAND_ITEM[i]['name']['kr'] for i in ids]
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_strict_names_and_korean_backend(self):
        code = '''
from unittest.mock import Mock, patch
from module.config.server import set_server
set_server('kr')
from module.island.order import IslandOrder
from module.island.data import DIC_ISLAND_ITEM
ui = Mock()
for name in ['신선한 고기', '숯불고기 꼬치']:
    ids = [k for k, v in DIC_ISLAND_ITEM.items() if v['name'].get('kr') == name]
    assert len(ids) == 1
    assert IslandOrder.item_name_to_item_id(ui, name) == ids[0]
    assert IslandOrder.item_name_to_item_id(ui, name.replace(' ', '')) == ids[0]
for name in ['', '???', '신선한 고가', None, 123]:
    assert IslandOrder.item_name_to_item_id(ui, name) is None
with patch.dict(DIC_ISLAND_ITEM, {1: {'name': {'kr': '중복'}}, 2: {'name': {'kr': '중복'}}}, clear=True):
    assert IslandOrder.item_name_to_item_id(ui, '중복') is None
ui.requirement_name_grid.buttons = []
ocr = IslandOrder.requirement_name_ocr.func(ui)
assert ocr.lang == 'ko'
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
