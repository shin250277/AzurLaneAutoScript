"""Localized selection controls must exclude occupied cards and safe click bounds."""
import ast
from pathlib import Path
import unittest


class SelectionAssetTest(unittest.TestCase):
    def test_tactical_confirm_click_stays_inside_visible_button(self):
        tree = ast.parse(Path('module/tactical/tactical_class.py').read_text(encoding='utf-8'))
        call = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'KR_SHIP_CONFIRM')
        area = ast.literal_eval(next(k.value for k in call.keywords if k.arg == 'button'))
        self.assertGreaterEqual(area[1], 641)
        self.assertLessEqual(area[3], 698)

    def test_occupied_marker_is_localized(self):
        tree = ast.parse(Path('module/island_handler/assets.py').read_text(encoding='utf-8'))
        call = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'TEMPLATE_ISLAND_DOCK_OCCUPIED')
        files = ast.literal_eval(call.keywords[0].value)
        self.assertEqual(files['kr'], './assets/kr/island_handler/TEMPLATE_ISLAND_DOCK_OCCUPIED.png')
        self.assertTrue(Path(files['kr']).is_file())


if __name__ == '__main__':
    unittest.main()
