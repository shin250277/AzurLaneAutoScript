"""Korean order requirements must reject uncertain item identities."""
import subprocess
import sys
import unittest


class KoreanOrderOcrTest(unittest.TestCase):
    def test_incomplete_requirement_scan_fails_closed(self):
        code = '''
from unittest.mock import Mock
from module.config.server import set_server
set_server('kr')
from module.island.order import IslandOrder
from module.exception import RequestHumanTakeover
ui = Mock()
ui.item_name_to_item_id.side_effect = lambda name: IslandOrder.item_name_to_item_id(ui, name)
cases = [
    (['철광석', '???', ''], [(43, 6, 37), (5, 1, 4), (0, 0, 0)]),
    (['철광석', '', ''], [(43, 6, 37), (5, 1, 4), (0, 0, 0)]),
    (['철광석', '', ''], [(0, 0, 0), (0, 0, 0), (0, 0, 0)]),
    (['철광석', '철광석', ''], [(43, 6, 37), (43, 2, 41), (0, 0, 0)]),
    (['', '', ''], [(0, 0, 0)] * 3),
    (['철광석', '', ''], [(43, 6, 37)]),
    (['철광석', '', ''], [None, (0, 0, 0), (0, 0, 0)]),
    (['철광석', '', ''], [(43, 6, 99), (0, 0, 0), (0, 0, 0)]),
]
for names, counters in cases:
    ui.requirement_name_ocr.ocr.return_value = names
    ui.requirement_counter_ocr.ocr.return_value = counters
    try:
        IslandOrder.scan_current_order_requirements(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Unsafe partial scan accepted: %r %r' % (names, counters))
ui.submit_order.assert_not_called()
ui.reject_order.assert_not_called()
ui.config.cross_set.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_complete_requirement_scan_keeps_stock_and_blank_rows(self):
        code = '''
from unittest.mock import Mock
from module.config.server import set_server
set_server('kr')
from module.island.order import IslandOrder
ui = Mock()
ui.item_name_to_item_id.side_effect = lambda name: IslandOrder.item_name_to_item_id(ui, name)
ui.requirement_name_ocr.ocr.return_value = ['철광석', '', '']
ui.requirement_counter_ocr.ocr.return_value = [(43, 6, 37), (0, 0, 0), (0, 0, 0)]
assert IslandOrder.scan_current_order_requirements(ui) == {2703: (43, 6, 37)}
ui.requirement_name_ocr.ocr.return_value = ['목초', '알루미늄 광석', '달걀']
ui.requirement_counter_ocr.ocr.return_value = [(0, 41, -41), (61, 1, 60), (519, 8, 511)]
assert IslandOrder.scan_current_order_requirements(ui) == {
    2008: (0, 41, -41), 2702: (61, 1, 60), 2601: (519, 8, 511)}
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

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
