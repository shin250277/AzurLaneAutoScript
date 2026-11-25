import subprocess
import sys
import unittest


class SoldOutPageTest(unittest.TestCase):
    def test_real_cards_and_negative_controls(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.clerk import kr_sold_out_page
import numpy as np
frame, items = scan_frame('dev_tools/fixtures/kr_event_shop_sold_out_cards.png')
assert len(items.grids.buttons) == 5
assert kr_sold_out_page(frame, items.grids)
shifted, shifted_items = scan_frame('dev_tools/fixtures/kr_event_shop_sold_out_shifted.png')
assert kr_sold_out_page(shifted, shifted_items.grids)
bottom, bottom_items = scan_frame('dev_tools/fixtures/kr_event_shop_sold_out_bottom.png')
assert len(bottom_items.grids.buttons) == 10
assert kr_sold_out_page(bottom, bottom_items.grids)
# One real card lacking its badge must not be mistaken for an empty last slot.
bottom[484:531, 284:316] = 255
assert not kr_sold_out_page(bottom, bottom_items.grids)
assert not kr_sold_out_page(np.full_like(frame, 255), items.grids)
assert not kr_sold_out_page(np.zeros_like(frame), items.grids)
changed = frame.copy()
b = items.grids.buttons[2]
x,y,r,bottom = b.area
changed[y:bottom,x:r] = 255
assert not kr_sold_out_page(changed, items.grids)
for source in ('kr_event_shop_top.png', 'kr_event_shop_design_counter.png',
               'kr_event_shop_middle.png', 'kr_event_shop_middle_shifted.png',
               'kr_event_shop_bottom.png', 'kr_event_shop_bottom_shifted.png'):
    frame, items = scan_frame('dev_tools/fixtures/' + source)
    assert not kr_sold_out_page(frame, items.grids), source
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
