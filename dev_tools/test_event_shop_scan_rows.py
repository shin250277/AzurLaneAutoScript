import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


def item(name, y, price=30, count=30):
    return SimpleNamespace(name=name, button=(266, y, 329, y + 63), price=price,
                           amount=1, cost='pt', count=count, total_count=30)


class ShopScanRowsTest(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path('module/shop_event/clerk.py').read_text(encoding='utf-8'))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'merge_scan_page')
        namespace = {}
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
