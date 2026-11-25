"""Refresh an event entrance after retirement changes the visible map mode."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class RetirementStageReturnTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/map/map_operation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MapOperation')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_refresh_stage_after_retirement')]
        scope = {'page_event': 'event'}
        exec(compile(tree, str(path), 'exec'), scope)
        self.refresh = scope['_kr_refresh_stage_after_retirement']
        self.original = SimpleNamespace(name='c3')
        self.fresh = SimpleNamespace(name='c3', area=None, button=(1, 2, 3, 4))
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  ui_page_appear=Mock(return_value=True),
                                  ensure_campaign_ui=Mock(), ENTRANCE=self.fresh)

    def test_event_return_reacquires_same_stage(self):
        self.assertIs(self.refresh(self.ui, self.original, 'hard'), self.fresh)
        self.ui.ensure_campaign_ui.assert_called_once_with(name='c3', mode='hard')
        self.assertEqual(self.fresh.area, self.fresh.button)
        self.assertIs(self.ui.stage_entrance, self.fresh)

    def test_other_return_screen_keeps_original(self):
        self.ui.ui_page_appear.return_value = False
        self.assertIs(self.refresh(self.ui, self.original, 'hard'), self.original)
        self.ui.ensure_campaign_ui.assert_not_called()

    def test_other_server_keeps_original(self):
        self.ui.config.SERVER = 'jp'
        self.assertIs(self.refresh(self.ui, self.original, 'hard'), self.original)
        self.ui.ui_page_appear.assert_not_called()
        self.ui.ensure_campaign_ui.assert_not_called()


if __name__ == '__main__':
    unittest.main()
