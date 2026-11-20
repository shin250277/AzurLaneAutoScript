from pathlib import Path
from types import SimpleNamespace
import unittest
import subprocess
import sys
from unittest.mock import Mock
import numpy as np
from module.base.utils import load_image, crop
from module.shop_event.korean_currency import KoreanEventCurrency, validated_point_items
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class EventCurrencyTest(unittest.TestCase):
    def test_current_guitar_header_and_card_references(self):
        reader = KoreanEventCurrency()
        paths = list(Path('assets/shop/event_kr_currency').glob('guitar_pt*.png'))
        self.assertGreaterEqual(len(paths), 11)
        for path in paths:
            self.assertEqual(reader.identify(load_image(str(path))), 'guitar_pt', str(path))

    def test_header_and_twenty_observed_price_tokens(self):
        # Server-sensitive generated assets must be imported in a fresh process.
        code = '''
from dev_tools.check_kr_event_shop_frame import scan_frame
from module.shop_event.korean_currency import KoreanEventCurrency, validated_point_items
from module.base.utils import crop
reader = KoreanEventCurrency()
for source, expected in [('kr_event_shop_top.png', 'train_pt'),
                         ('kr_event_shop_design_counter.png', 'skull_pt')]:
    frame, grid = scan_frame('dev_tools/fixtures/' + source)
    for button in grid.grids.buttons:
        x, y = button.area[:2]
        assert reader.identify(crop(frame, (x-17,y+120,x+35,y+149))) == expected
    if expected == 'train_pt':
        assert reader.identify(crop(frame, (935,155,985,190))) == expected
        grid.predict(frame, save_unknown=False)
        assert validated_point_items(grid.items, expected)
for source in ('kr_event_shop_middle.png', 'kr_event_shop_middle_shifted.png',
               'kr_event_shop_bottom.png', 'kr_event_shop_bottom_shifted.png'):
    frame, grid = scan_frame('dev_tools/fixtures/' + source)
    grid.predict(frame, save_unknown=False)
    assert all(item.kr_currency_token == 'train_pt' for item in grid.items), source
    assert validated_point_items(grid.items, 'train_pt'), source
    if source == 'kr_event_shop_bottom_shifted.png':
        assert (grid.items[-1].count, grid.items[-1].total_count) == (100,100)
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_diamonds_blank_and_unrelated_currency_are_rejected(self):
        reader = KoreanEventCurrency()
        for path in Path('assets/shop/cost').glob('*.png'):
            self.assertIsNone(reader.identify(load_image(str(path))), str(path))
        for value in (0, 128, 255):
            self.assertIsNone(reader.identify(np.full((35,52,3), value, dtype=np.uint8)))
        self.assertIsNone(reader.identify(np.random.RandomState(17).randint(0,256,(35,52,3),dtype=np.uint8)))

    def test_unknown_mixed_currency_or_invalid_counter_blocks(self):
        base = dict(kr_currency_token='train_pt', cost='pt', price=200, amount=1, count=2, total_count=3)
        self.assertTrue(validated_point_items([SimpleNamespace(**base)], 'train_pt'))
        for key, value in [('kr_currency_token', None), ('kr_currency_token', 'skull_pt'),
                           ('cost', 'Gems'), ('price', 0), ('amount', True),
                           ('count', 4), ('total_count', -1)]:
            row = dict(base)
            row[key] = value
            self.assertFalse(validated_point_items([SimpleNamespace(**row)], 'train_pt'))
        self.assertFalse(validated_point_items([], 'train_pt'))
        zero = dict(base, count=0, total_count=0)
        self.assertFalse(validated_point_items([SimpleNamespace(**zero)], 'train_pt'))
        self.assertFalse(validated_point_items([SimpleNamespace(**base)], None))

    def test_direct_purchase_entry_rejects_before_any_input(self):
        run = method('module/shop_event/clerk.py', 'EventShopClerk', 'event_shop_buy_item_execute',
                     validated_point_items=validated_point_items)
        ui = Mock()
        ui.config.SERVER = 'kr'
        with self.assertRaises(TaskStopped):
            run(ui, SimpleNamespace(), amount=1)
        ui.device.click.assert_not_called()
        ui.event_shop_handle_obstruct.assert_not_called()

    def test_fresh_scan_currency_or_amount_change_prevents_purchase(self):
        class MissingItem(Exception):
            pass
        run = method('module/shop_event/clerk.py', 'EventShopClerk', 'event_shop_buy_item',
                     validated_point_items=validated_point_items,
                     EVENT_SHOP_SCROLL=Mock(), ItemNotFoundError=MissingItem)
        base = dict(name='Oil', kr_currency_token='train_pt', cost='pt', price=200,
                    amount=1000, count=2, total_count=3, scroll_pos=0.5, is_ship=False)
        for changed in (dict(kr_currency_token=None), dict(cost='Gems'), dict(amount=2000)):
            ui = Mock()
            ui.config.SERVER = 'kr'
            fresh = dict(base)
            fresh.update(changed)
            ui.event_shop_get_items.return_value = [SimpleNamespace(**fresh)]
            with self.assertRaises(MissingItem):
                run(ui, SimpleNamespace(**base), amount=1)
            ui.event_shop_buy_item_execute.assert_not_called()

    def test_unchanged_fresh_scan_preserves_explicit_purchase_amount(self):
        run = method('module/shop_event/clerk.py', 'EventShopClerk', 'event_shop_buy_item',
                     validated_point_items=validated_point_items,
                     EVENT_SHOP_SCROLL=Mock(), ItemNotFoundError=RuntimeError)
        item = SimpleNamespace(name='Oil', kr_currency_token='train_pt', cost='pt', price=200,
                               amount=1000, count=2, total_count=3, scroll_pos=0.5, is_ship=False)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.event_shop_get_items.return_value = [item]
        run(ui, item, amount=1)
        ui.event_shop_buy_item_execute.assert_called_once_with(item, amount=1)


if __name__ == '__main__':
    unittest.main()
