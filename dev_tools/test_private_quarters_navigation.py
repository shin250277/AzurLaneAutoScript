"""Shop transitions must use localized private quarters page detection."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock


class PrivateQuartersNavigationTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/private_quarters/private_quarters.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PrivateQuarters')
        tree.body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                     and n.name in ('_pq_shop_enter', '_pq_shop_exit')]
        scope = {n.id: n.id for n in ast.walk(tree)
                 if isinstance(n, ast.Name) and n.id.isupper()}
        scope['page_private_quarters'] = 'localized_quarters'
        exec(compile(tree, str(path), 'exec'), scope)
        self.methods = scope
        self.ui = Mock()

    def test_enter_uses_localized_appear_check(self):
        self.methods['_pq_shop_enter'](self.ui)
        check = self.ui.ui_click.call_args[1]['appear_button']
        self.assertTrue(callable(check))
        check()
        self.ui.ui_page_appear.assert_called_once_with('localized_quarters')

    def test_exit_uses_localized_completion_check(self):
        self.methods['_pq_shop_exit'](self.ui)
        check = self.ui.ui_click.call_args[1]['check_button']
        self.assertTrue(callable(check))
        check()
        self.ui.ui_page_appear.assert_called_once_with('localized_quarters')


if __name__ == '__main__':
    unittest.main()
