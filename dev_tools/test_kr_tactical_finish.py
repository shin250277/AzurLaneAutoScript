"""Device-free guards for the Korean tactical completion receipt."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class TacticalFinishTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/tactical/tactical_class.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'RewardTacticalClass')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'handle_kr_tactical_finish')]
        self.confirm = SimpleNamespace(color=(64, 123, 194))
        scope = {'KR_TACTICAL_FINISH_HEADER': SimpleNamespace(color=(73, 117, 175)),
                 'KR_TACTICAL_FINISH_CONFIRM': self.confirm}
        exec(compile(tree, str(path), 'exec'), scope)
        self.handle = scope['handle_kr_tactical_finish']
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  image_color_count=Mock(), device=SimpleNamespace(click=Mock()))

    def test_other_server_never_clicks(self):
        self.ui.config.SERVER = 'jp'
        self.assertFalse(self.handle(self.ui))
        self.ui.image_color_count.assert_not_called()
        self.ui.device.click.assert_not_called()

    def test_missing_header_never_clicks(self):
        self.ui.image_color_count.return_value = False
        self.assertFalse(self.handle(self.ui))
        self.ui.device.click.assert_not_called()

    def test_header_without_button_never_clicks(self):
        self.ui.image_color_count.side_effect = [True, False]
        self.assertFalse(self.handle(self.ui))
        self.ui.device.click.assert_not_called()

    def test_complete_receipt_clicks_only_confirmation(self):
        self.ui.image_color_count.side_effect = [True, True]
        self.assertTrue(self.handle(self.ui))
        self.ui.device.click.assert_called_once_with(self.confirm)


if __name__ == '__main__':
    unittest.main()
