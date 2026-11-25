"""KR favourite recognition must tolerate the empty-list overlay only in dock."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class BaseSwitch:
    def get(self, main):
        return 'base-result'


class DockFavouriteTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/retire/dock.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'DockFavouriteSwitch']
        scope = {'Switch': BaseSwitch, 'page_dock': object()}
        exec(compile(tree, str(path), 'exec'), scope)
        self.switch = scope['DockFavouriteSwitch']()
        self.switch.state_list = [dict(state='on', check_button=(212, 171, 129)),
                                  dict(state='off', check_button=(119, 131, 170))]
        self.main = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                    ui_page_appear=Mock(return_value=True), appear=Mock())

    def use_color(self, color):
        self.main.appear.side_effect = lambda expected, offset, threshold: max(
            abs(a-b) for a, b in zip(color, expected)) <= threshold

    def test_darkened_off(self):
        self.use_color((107, 122, 162))
        self.assertEqual(self.switch.get(self.main), 'off')

    def test_on_remains_distinct(self):
        self.use_color((212, 171, 129))
        self.assertEqual(self.switch.get(self.main), 'on')

    def test_unknown_color(self):
        self.use_color((0, 0, 0))
        self.assertEqual(self.switch.get(self.main), 'unknown')

    def test_outside_dock(self):
        self.main.ui_page_appear.return_value = False
        self.assertEqual(self.switch.get(self.main), 'unknown')
        self.main.appear.assert_not_called()

    def test_other_servers_unchanged(self):
        self.main.config.SERVER = 'jp'
        self.assertEqual(self.switch.get(self.main), 'base-result')
        self.main.ui_page_appear.assert_not_called()


if __name__ == '__main__':
    unittest.main()
