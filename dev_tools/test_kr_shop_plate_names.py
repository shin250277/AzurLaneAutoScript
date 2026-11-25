"""Korean text must disambiguate visually similar plate icons."""
import subprocess
import sys
import unittest


class PlateNameTest(unittest.TestCase):
    def test_entire_observed_scroll_sequence(self):
        code = '''
import module.config.server as server
server.server = 'kr'
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.clerk import merge_scan_page
items, last = [], []
for number in range(1, 9):
    frame, grid = scan_frame('dev_tools/fixtures/kr_shop_oct02_sequence/%02d.png' % number)
    grid.predict(frame, save_unknown=False)
    items, last = merge_scan_page(items, last, grid.items)
assert len(items) == 32, len(items)
assert not any(item.name.isdigit() for item in items)
assert all(item.total_count > 0 for item in items)
assert [item.name for item in items[24:29]] == ['PlateGeneralT3', 'PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3']
assert [(i.name, i.amount) for i in items[11:13]] == [('PRSeriesUnknown', 1), ('DRSeriesUnknown', 1)]
'''
        run = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=45)
        self.assertEqual(run.returncode, 0, run.stdout.decode('utf-8', errors='replace'))

    def test_observed_labels_and_blank(self):
        code = '''
import numpy as np
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.korean_names import KoreanShopNames
from module.base.utils import load_image
reader = KoreanShopNames()
for name in ('PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3', 'PlateGeneralT3'):
    assert reader.match(load_image('assets/shop/event_kr_names/' + name + '.png')) == name
assert reader.match(np.full((28, 152, 3), 200, dtype=np.uint8)) is None
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_plate_raster.png')
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items[:4]] == ['PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3']
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_general_label.png')
grid.predict(frame, save_unknown=False)
assert grid.items[-1].name == 'PlateGeneralT3'
frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_plate_raster.png')
for button in grid.grids.buttons[:4]:
    x, y = button.area[:2]
    frame[y+72:y+100, x-44:x+108] = 200
grid.predict(frame, save_unknown=False)
assert [i.name for i in grid.items[:4]] == ['PlateUnknown'] * 4
'''
        run = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout.decode('utf-8', errors='replace'))
