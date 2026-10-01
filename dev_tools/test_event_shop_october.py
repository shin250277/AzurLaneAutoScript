"""Regression for observed October KR shop failures, without device input."""
import subprocess
import sys
import unittest


class OctoberShopTest(unittest.TestCase):
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
