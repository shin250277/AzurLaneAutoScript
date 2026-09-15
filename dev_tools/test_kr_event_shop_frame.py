"""Regression on sanitized, observed KR event-shop pixels (no device input)."""
import subprocess
import sys
import unittest


class EventShopFrameTest(unittest.TestCase):
    def test_middle_page_distinguishes_all_three_plate_icons(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_middle.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items] == ['BoxT4', 'BoxT4', 'PlateGeneralT3', 'PlateGunT3', 'PlateTorpedoT3'], [i.name for i in grid.items]
assert [i.amount for i in grid.items] == [1] * 5
assert [i.price for i in grid.items] == [300, 300, 30, 30, 30]
assert [i.count for i in grid.items] == [4, 4, 30, 30, 30]
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_middle_shifted.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items] == ['BoxT4', 'BoxT4', 'PlateGeneralT3', 'PlateGunT3', 'PlateTorpedoT3'], [i.name for i in grid.items]
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_bottom_shifted.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items] == ['PlateAntiairT3', 'PlatePlaneT3', 'Coin', 'Oil', 'FoodT1'], [i.name for i in grid.items]
'''
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_diagnostic_uses_runtime_predictions_without_saving_unknown_icons(self):
        code = '''
from unittest.mock import patch
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_top.png')
with patch('module.base.utils.save_image') as save:
    grid.predict(frame, save_unknown=False)
    assert grid.items[1].amount == 1
    assert grid.items[1].total_count == 10
    unknown = grid.items[-1]
    unknown.name, unknown.price, unknown.total_count = '999999', 123, 7
    unknown.correct_name_and_cost(save_unknown=False)
    save.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_cli_reports_corrected_skinbox_amount(self):
        result = subprocess.run([sys.executable, '-m', 'dev_tools.check_kr_event_shop_frame',
                                 'dev_tools/fixtures/kr_event_shop_top.png'],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.stdout.decode('utf-8', errors='replace')
        self.assertEqual(result.returncode, 0, output)
        self.assertIn('SkinBox_x1_10/10_pt_x2000', output)

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
