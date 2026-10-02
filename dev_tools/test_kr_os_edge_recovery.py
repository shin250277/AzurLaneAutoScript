"""Bounded KR OpSi vertical-edge fallback; no live device interaction."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class EdgeRecoveryTest(unittest.TestCase):
    def recover(self, server='kr', task='OpsiExplore', candidate=(874, None, None, 758), count=(1, 1)):
        path = Path('module/map_detection/homography.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == '_recover_kr_os_vertical_edge')
        tree.body = [method]
        scope = dict(logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        obj = SimpleNamespace(config=SimpleNamespace(SERVER=server, Scheduler_Command=task,
                              HOMO_EDGE_HOUGHLINES_THRESHOLD=300),
                              left_edge=None, right_edge=None, lower_edge=None,
                              upper_edge=758, _map_edge_count=(0, 1))
        def detect(image, hough_th):
            obj.left_edge, obj.right_edge, obj.lower_edge, obj.upper_edge = candidate
            obj._map_edge_count = count
        obj.detect_edges = Mock(side_effect=detect)
        scope['_recover_kr_os_vertical_edge'](obj, 'edge mask')
        return obj

    def test_recovers_unique_aligned_vertical_edge(self):
        obj = self.recover()
        self.assertEqual(obj.left_edge, 874)
        obj.detect_edges.assert_called_once_with('edge mask', hough_th=240)

    def test_does_not_change_other_servers_or_normal_maps(self):
        for server, task in [('jp', 'OpsiExplore'), ('kr', 'Main')]:
            self.recover(server, task).detect_edges.assert_not_called()

    def test_rejects_ambiguous_vertical_lines(self):
        obj = self.recover(count=(2, 1))
        self.assertIsNone(obj.left_edge)
        self.assertEqual(obj._map_edge_count, (0, 1))

    def test_rejects_changed_horizontal_boundary(self):
        obj = self.recover(candidate=(874, None, None, 700))
        self.assertIsNone(obj.left_edge)
        self.assertEqual(obj.upper_edge, 758)


if __name__ == '__main__':
    unittest.main()
