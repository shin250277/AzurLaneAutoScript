"""A research title behind a detail overlay is not the project list."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class ResearchDetailGuardTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/research/ui.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ResearchUI')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'is_in_research')]
        scope = dict(page_research='page', RESEARCH_START='start',
                     RESEARCH_STOP='stop', RESEARCH_UNAVAILABLE='unavailable')
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['is_in_research']
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  ui_page_appear=Mock(return_value=True),
                                  appear=Mock(return_value=False))

    def test_detail_controls_exclude_visible_background_title(self):
        for control in ('start', 'stop', 'unavailable'):
            with self.subTest(control=control):
                self.ui.appear.side_effect = lambda button, **kwargs: button == control
                self.assertFalse(self.check(self.ui))

    def test_list_without_detail_controls_is_allowed(self):
        self.assertTrue(self.check(self.ui))

    def test_missing_title_is_not_the_list(self):
        self.ui.ui_page_appear.return_value = False
        self.assertFalse(self.check(self.ui))

    def test_other_servers_keep_original_page_detection(self):
        self.ui.config.SERVER = 'jp'
        self.assertTrue(self.check(self.ui, interval=3))
        self.ui.appear.assert_not_called()
        self.ui.ui_page_appear.assert_called_once_with('page', offset=(20, 20), interval=3)


if __name__ == '__main__':
    unittest.main()
