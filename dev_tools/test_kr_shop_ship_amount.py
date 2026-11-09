import subprocess
import sys
import unittest
from unittest.mock import Mock, patch


class ShipAmountTest(unittest.TestCase):
    def test_narrow_quantity_requires_two_positive_agreeing_reads(self):
        import module.config.server as server
        from module.shop_event.item import EventShopItemGrid
        from module.statistics.item import ItemGrid
        for result in ([1, 2], [0, 0], [1]):
            item = Mock(name='ship')
            item.name, item.amount, item.is_ship = 'ShipSSR', 21, True
            grid = EventShopItemGrid.__new__(EventShopItemGrid)
            grid.items, grid.kr_names = [item], None
            grid.amount_ocr = Mock()
            grid.amount_ocr.ocr.return_value = result
            with patch.object(server, 'server', 'kr'), patch.object(ItemGrid, 'predict'):
                grid.predict(None, counter=False, save_unknown=False)
            self.assertEqual(item.amount, 21)

    def test_non_ship_and_foreign_amounts_keep_original_crop(self):
        import module.config.server as server
        from module.shop_event.item import EventShopItemGrid
        from module.statistics.item import ItemGrid
        for region, is_ship, name in [('kr', False, 'Oil'), ('jp', True, 'ShipSSR')]:
            item = Mock()
            item.name, item.amount, item.is_ship = name, 1000, is_ship
            grid = EventShopItemGrid.__new__(EventShopItemGrid)
            grid.items, grid.kr_names = [item], None
            grid.amount_ocr = Mock()
            with patch.object(server, 'server', region), patch.object(ItemGrid, 'predict'):
                grid.predict(None, counter=False, save_unknown=False)
            grid.amount_ocr.ocr.assert_not_called()
            self.assertEqual(item.amount, 1000)

    def test_public_ship_card_decoration_is_not_quantity(self):
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
frame, grid = scan_frame('dev_tools/fixtures/kr_shop_ship_nov9.png')
grid.predict(frame, save_unknown=False)
assert len(grid.items) == 1, len(grid.items)
item = grid.items[0]
assert (item.name, item.amount, item.price, item.count, item.total_count) == ('ShipSSR', 1, 8000, 5, 5), str(item)
'''
        run = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout.decode('utf-8', errors='replace'))
