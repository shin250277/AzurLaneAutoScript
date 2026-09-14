"""Regression on sanitized, observed KR event-shop pixels (no device input)."""
import subprocess
import sys
import unittest


class EventShopFrameTest(unittest.TestCase):
    def test_top_page_amounts_and_prices(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_top.png')
grid.predict(frame)
assert [i.amount for i in grid.items] == [1, 1, 100, 10, 1, 1, 1, 1, 1, 1], [i.amount for i in grid.items]
assert [i.price for i in grid.items] == [8000, 2000, 300, 1000, 500, 1000, 250, 500, 3000, 300]
from module.shop_event.ui import OCR_EVENT_SHOP_PT
assert OCR_EVENT_SHOP_PT.ocr(frame) == 4720
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_bottom.png')
grid.predict(frame)
assert [i.amount for i in grid.items] == [1, 1, 2000, 1000, 1], [i.amount for i in grid.items]
assert [i.name for i in grid.items] == ['PlateAntiairT3', 'PlatePlaneT3', 'Coin', 'Oil', 'FoodT1'], [i.name for i in grid.items]
'''
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
