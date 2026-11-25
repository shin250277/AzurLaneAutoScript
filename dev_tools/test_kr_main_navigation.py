"""Device-free regression tests for KR's main navigation guard."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def navigation_method():
    # Load only this method: importing UI would initialize OCR/game assets.
    source = Path(__file__).resolve().parents[1] / 'module/ui/ui.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    ui = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'UI')
    method = next(node for node in ui.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'ui_main_appear_then_click')
    tree.body = [method]
    destination = object()
    main = object()
    button = object()
    namespace = {'page_main': main,
                 'page_main_white': SimpleNamespace(links={destination: button})}
    exec(compile(tree, str(source), 'exec'), namespace)
    return namespace['ui_main_appear_then_click'], destination, main, button


class MainNavigationTest(unittest.TestCase):
    def setUp(self):
        self.navigate, self.destination, self.main, self.button = navigation_method()
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  ui_page_appear=Mock(), device=SimpleNamespace(click=Mock()))

    def test_destination_already_open_does_not_click(self):
        self.ui.ui_page_appear.return_value = True
        self.assertFalse(self.navigate(self.ui, self.destination))
        self.ui.device.click.assert_not_called()

    def test_other_foreground_page_does_not_click_main_menu(self):
        self.ui.ui_page_appear.side_effect = [False, False]
        self.assertFalse(self.navigate(self.ui, self.destination))
        self.ui.ui_page_appear.assert_called_with(self.main, offset=(30, 30), interval=3)
        self.ui.device.click.assert_not_called()

    def test_actual_main_page_clicks_destination(self):
        self.ui.ui_page_appear.side_effect = [False, True]
        self.assertTrue(self.navigate(self.ui, self.destination))
        self.ui.device.click.assert_called_once_with(self.button)


if __name__ == '__main__':
    unittest.main()
