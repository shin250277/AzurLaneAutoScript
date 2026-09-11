import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class KrGetShipGuardTest(unittest.TestCase):
    def test_white_patch_is_never_clicked_on_kr(self):
        path = Path('module/combat/combat.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'handle_get_ship')
        tree.body = [method]
        scope = {'GET_SHIP': 'white', 'NEW_SHIP': 'new', 'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        for server, card, result, fallback in [('kr', False, False, 0), ('kr', True, True, 0), ('jp', False, True, 1)]:
            ui = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                 handle_kr_ship_card=Mock(return_value=card),
                                 appear_then_click=Mock(return_value=True), appear=Mock(return_value=False))
            self.assertEqual(scope['handle_get_ship'](ui), result)
            self.assertEqual(ui.appear_then_click.call_count, fallback)
