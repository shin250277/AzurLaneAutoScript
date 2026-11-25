import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class KrAutoSearchShopTest(unittest.TestCase):
    def test_quit_shop_only_on_confirmed_kr_supply_screen(self):
        path = Path('module/os_handler/map_event.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'MapEventHandler')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                      and n.name == 'handle_kr_auto_search_shop_exit')
        tree.body = [method]
        scope = {'PORT_SUPPLY_CHECK': 'supply', 'BACK_ARROW': 'back', 'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        for server, visible, expected in [('kr', True, True), ('kr', False, False),
                                          ('jp', True, False)]:
            instance = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                       appear=Mock(return_value=visible), device=Mock())
            self.assertEqual(scope[method.name](instance), expected)
            if expected:
                instance.device.click.assert_called_once_with('back')
            else:
                instance.device.click.assert_not_called()

    def test_exit_is_wired_into_auto_search_quit(self):
        tree = ast.parse(Path('module/os_handler/map_event.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'os_auto_search_quit')
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                            and n.func.attr == 'handle_kr_auto_search_shop_exit'
                            for n in ast.walk(method)))
