import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


def item(name, y, price=30, count=30):
    return SimpleNamespace(name=name, button=(266, y, 329, y + 63), price=price,
                           amount=1, cost='pt', count=count, total_count=30)


class ShopScanRowsTest(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path('module/shop_event/clerk.py').read_text(encoding='utf-8'))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'merge_scan_page')
        import cv2
        namespace = {'cv2': cv2}
        exec(compile(ast.Module(body=[function]), '<rows>', 'exec'), namespace)
        self.merge = namespace['merge_scan_page']

    def test_reused_screen_y_does_not_collect_historical_rows(self):
        first, last = self.merge([], [], [item('A', 239), item('B', 463)])
        second, last = self.merge(first, last, [item('C', 239)])
        third, last = self.merge(second, last, [item('C', 350), item('D', 574)])
        self.assertEqual([i.name for i in third], ['A', 'B', 'C', 'D'])

    def test_repeated_last_row_uses_fresh_counter(self):
        old = item('Food', 401, count=0)
        new = item('Food', 239, count=30)
        result, last = self.merge([old], [old], [new])
        self.assertEqual(result, [new])

    def test_same_name_with_different_price_is_not_duplicate(self):
        old, new = item('Box', 239, price=300), item('Box', 350, price=500)
        result, _ = self.merge([old], [old], [new])
        self.assertEqual(result, [old, new])

    def test_empty_page_is_explicitly_rejected(self):
        with self.assertRaises(ValueError):
            self.merge([], [], [])

    def test_adjacent_identical_icons_survive_name_ocr_disagreement(self):
        import numpy as np
        old, new = item('WrongPlate', 424), item('PlatePlaneT3', 248)
        old.image = np.random.RandomState(7).randint(0, 256, (63, 63, 3)).astype('uint8')
        new.image = old.image.copy()
        result, _ = self.merge([old], [old], [new])
        self.assertEqual(result, [new])

    def test_different_icons_with_same_price_remain_distinct(self):
        import numpy as np
        old, new = item('A', 424), item('B', 248)
        old.image = np.random.RandomState(7).randint(0, 256, (63, 63, 3)).astype('uint8')
        new.image = np.random.RandomState(8).randint(0, 256, (63, 63, 3)).astype('uint8')
        result, _ = self.merge([old], [old], [new])
        self.assertEqual(result, [old, new])

    def scan(self, server, bottom):
        tree = ast.parse(Path('module/shop_event/clerk.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'EventShopClerk')
        function = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'scan_all')
        scroll = Mock()
        scroll.at_bottom.side_effect = bottom
        namespace = dict(EVENT_SHOP_SCROLL=scroll, logger=Mock(),
                         merge_scan_page=self.merge, RequestHumanTakeover=RuntimeError)
        exec(compile(ast.Module(body=[function]), '<scan>', 'exec'), namespace)
        clerk = Mock()
        clerk.config.SERVER = server
        clerk.event_shop_get_items.return_value = [item('A', 239)]
        return namespace['scan_all'], clerk, scroll

    def test_kr_scroll_keeps_full_rows_visible(self):
        scan, clerk, scroll = self.scan('kr', [False, True])
        scan(clerk)
        scroll.next_page.assert_called_once_with(main=clerk, page=0.4)

    def test_other_servers_keep_scroll_stride(self):
        scan, clerk, scroll = self.scan('cn', [False, True])
        scan(clerk)
        scroll.next_page.assert_called_once_with(main=clerk, page=0.66)

    def test_scan_has_bounded_attempts(self):
        scan, clerk, scroll = self.scan('kr', [False] * 41 + [True])
        with self.assertRaisesRegex(RuntimeError, 'bottom'):
            scan(clerk)
