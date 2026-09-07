"""Reject blue dock artwork unless the localized rarity warning is present."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class RetirementConfirmationTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/retire/retirement.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'Retirement')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_retirement_confirmation_appear')]
        scope = {'KR_RETIRE_RARITY_WARNING': 'warning',
                 'KR_RETIRE_SR_SSR_CONFIRM': SimpleNamespace(color=(83, 143, 207))}
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['_kr_retirement_confirmation_appear']
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  appear=Mock(return_value=True),
                                  image_color_count=Mock(return_value=True))

    def test_other_server_is_not_handled(self):
        self.ui.config.SERVER = 'jp'
        self.assertFalse(self.check(self.ui))
        self.ui.appear.assert_not_called()

    def test_blue_art_without_warning_is_not_a_dialog(self):
        self.ui.appear.return_value = False
        self.assertFalse(self.check(self.ui))
        self.ui.image_color_count.assert_not_called()

    def test_warning_without_confirm_is_not_a_dialog(self):
        self.ui.image_color_count.return_value = False
        self.assertFalse(self.check(self.ui))

    def test_warning_and_button_are_required(self):
        self.assertTrue(self.check(self.ui))
        self.ui.appear.assert_called_once_with('warning', offset=(3, 3), similarity=0.85)


if __name__ == '__main__':
    unittest.main()
