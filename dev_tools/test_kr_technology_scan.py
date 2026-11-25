"""Unmatched technology maps must not become production configuration."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class TechnologyScanTest(unittest.TestCase):
    def run_position(self, similarity):
        from module.exception import RequestHumanTakeover
        tree = ast.parse(Path('module/island_handler/technology_scanner.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'get_technology_view_position')]
        scope = dict(load_image=Mock(), extract_flowchart=Mock(), logger=Mock(),
                     np=__import__('numpy'), RequestHumanTakeover=RequestHumanTakeover,
                     cv2=SimpleNamespace(matchTemplate=Mock(), TM_CCOEFF_NORMED=5,
                         minMaxLoc=Mock(return_value=(0, similarity, (0, 0), (120, 0)))))
        exec(compile(tree, 'technology_scanner.py', 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock())
        return scope['get_technology_view_position'](ui, 2)

    def test_low_confidence_is_rejected(self):
        from module.exception import RequestHumanTakeover
        with self.assertRaises(RequestHumanTakeover):
            self.run_position(0.2)

    def test_invalid_confidence_is_rejected(self):
        from module.exception import RequestHumanTakeover
        with self.assertRaises(RequestHumanTakeover):
            self.run_position(float('nan'))

    def test_matching_chart_returns_position(self):
        self.assertEqual(self.run_position(0.95), 120)
