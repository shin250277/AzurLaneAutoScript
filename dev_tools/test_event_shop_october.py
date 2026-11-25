"""Regression for observed October KR shop failures, without device input."""
import subprocess
import sys
import unittest


class OctoberShopTest(unittest.TestCase):
    def test_blueprint_artwork_is_not_amount_digits(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_blueprint_amount.png')
grid.predict(frame, save_unknown=False)
assert grid.items[2].name == 'DRSeriesUnknown'
assert grid.items[2].amount == 1, str(grid.items[2])
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_fractional_scroll_icon_matching(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
for fixture in ('design_raster', 'design_counter'):
    frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_' + fixture + '.png')
    grid.predict(frame, save_unknown=False)
    assert grid.items[2].name == 'Design152mmMKXXVIT3', str(grid.items[2])
    assert grid.items[3].name == 'SkinBox', str(grid.items[3])
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_plate_raster.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items] == ['PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3', 'Coin']
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_generic_blueprint_icon_does_not_claim_series_eight(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.selector import FILTER_REGEX
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_design_counter.png')
grid.predict(frame, save_unknown=False)
for item, expected in zip(grid.items[6:8], ('PRSeriesUnknown', 'DRSeriesUnknown')):
    assert item.name == expected, str(item)
    assert not FILTER_REGEX.fullmatch(item.name.lower())
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_blueprint_unknown.png')
grid.predict(frame, save_unknown=False)
assert grid.items[1].name == 'PRSeriesUnknown', str(grid.items[1])
assert grid.items[2].name == 'DRSeriesUnknown', str(grid.items[2])
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_shifted_design_and_augment_amount(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_design_shifted.png')
grid.predict(frame, save_unknown=False)
assert grid.items[2].name == 'Design152mmMKXXVIT3', str(grid.items[2])
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_augment.png')
grid.predict(frame, save_unknown=False)
assert grid.items[-1].name == 'AugmentChangeT2'
assert grid.items[-1].amount == 1, str(grid.items[-1])
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_design_icon_is_not_a_complete_equipment_or_auto_buy_target(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.selector import FILTER_REGEX
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_design.png')
grid.predict(frame, save_unknown=False)
item = grid.items[7]
assert item.name == 'Design152mmMKXXVIT3', str(item)
assert (item.price, item.count, item.total_count, item.cost) == (135, 15, 15, 'pt'), str(item)
assert grid.items[6].name == 'EquipUR'
assert not FILTER_REGEX.fullmatch(item.name.lower())
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_october_plate_icons(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_october_plates.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items] == ['PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3', 'Coin'], [i.name for i in grid.items]
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_shifted_prices_exclude_currency_icon(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_october_shifted.png')
grid.predict(frame, save_unknown=False)
assert [i.price for i in grid.items] == [300, 300, 300, 300, 30], [i.price for i in grid.items]
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_bottom_overshoot_finishes_without_another_swipe(self):
        code = '''
from unittest.mock import Mock
import module.config.server as server
server.server = 'kr'
from module.shop_event.ui import EVENT_SHOP_SCROLL
EVENT_SHOP_SCROLL.cal_position = Mock(return_value=0.99)
main = Mock()
assert EVENT_SHOP_SCROLL.set(0.9, main) == 0
main.device.swipe.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
