import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class GlobalShipCardTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/ui/ui.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'UI')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'ui_handle_kr_ship_card')]
        scope = dict(KR_UI_SHIP_CARD='card', NEW_SHIP='new')
        exec(compile(tree, str(path), 'exec'), scope)
        self.handle = scope['ui_handle_kr_ship_card']

    def test_existing_card_dismissed_without_new_ship_flag(self):
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr', GET_SHIP_TRIGGERED=False),
                             appear=Mock(side_effect=[True, False]), device=Mock())
        self.assertTrue(self.handle(ui))
        ui.device.click.assert_called_once_with('card')
        self.assertFalse(ui.config.GET_SHIP_TRIGGERED)

    def test_missing_card_and_other_server_never_click(self):
        for server in ('kr', 'jp'):
            ui = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                 appear=Mock(return_value=False), device=Mock())
            self.assertFalse(self.handle(ui))
            ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
