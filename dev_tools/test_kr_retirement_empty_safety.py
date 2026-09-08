"""An empty KR quick retirement must not broaden the user's filters."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class EmptyRetirementSafetyTest(unittest.TestCase):
    def test_empty_kr_selection_stops_before_filter_changes(self):
        path = Path(__file__).resolve().parents[1] / 'module/retire/retirement.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'Retirement')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_retire_handler')]
        scope = {'RequestHumanTakeover': RuntimeError, 'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'),
            retire_ships_one_click=Mock(return_value=0),
            dock_favourite_set=Mock(), dock_filter_set=Mock())
        with self.assertRaisesRegex(RuntimeError, 'no eligible ships'):
            scope['_retire_handler'](ui, mode='one_click_retire')
        ui.retire_ships_one_click.assert_called_once_with()
        ui.dock_favourite_set.assert_not_called()
        ui.dock_filter_set.assert_not_called()


if __name__ == '__main__':
    unittest.main()
