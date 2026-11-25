"""Reject a short fog boundary paired with a well-supported outer edge."""
import ast
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

import numpy as np


class HorizontalEdgeTest(unittest.TestCase):
    def recover(self, support=(1., .4), server='kr', task='OpsiDaily', span=420,
                valid_width=1000, missing=False):
        path = Path('module/map_detection/homography.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == '_reject_kr_os_internal_horizontal_edge')
        tree.body = [method]
        scope = dict(np=np, logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        lower, upper = 100, 100 + span
        image = np.zeros((1600, 1100), dtype=np.uint8)
        mask = np.zeros_like(image)
        mask[:, :valid_width] = 255
        for row, ratio in zip((lower, upper), support):
            image[row, :int(valid_width * ratio)] = 255
        obj = SimpleNamespace(config=SimpleNamespace(SERVER=server,
                              Scheduler_Command=task, HOMO_TILE=(140, 140)),
                              lower_edge=None if missing else lower, upper_edge=upper,
                              left_edge=None, right_edge=1000,
                              ui_mask_homo_stroke=mask)
        scope['_reject_kr_os_internal_horizontal_edge'](obj, image)
        return obj

    def test_keeps_strong_top_and_rejects_fog_line(self):
        obj = self.recover()
        self.assertEqual(obj.lower_edge, 100)
        self.assertIsNone(obj.upper_edge)

    def test_symmetric_bottom_edge(self):
        obj = self.recover(support=(.4, 1.))
        self.assertIsNone(obj.lower_edge)
        self.assertEqual(obj.upper_edge, 520)

    def test_preserves_ambiguous_edges(self):
        for support in [(1., 1.), (.4, .4), (.8, .4), (1., .7)]:
            obj = self.recover(support=support)
            self.assertEqual((obj.lower_edge, obj.upper_edge), (100, 520))

    def test_preserves_other_servers_tasks_and_wide_maps(self):
        for kwargs in [dict(server='jp'), dict(task='Main'), dict(span=1120),
                       dict(valid_width=200)]:
            obj = self.recover(**kwargs)
            self.assertIsNotNone(obj.lower_edge)
            self.assertIsNotNone(obj.upper_edge)

    def test_single_edge_is_unchanged(self):
        obj = self.recover(missing=True)
        self.assertIsNone(obj.lower_edge)
        self.assertEqual(obj.upper_edge, 520)

    def test_known_opsi_maps_cannot_fit_between_short_pair(self):
        tree = ast.parse(Path('module/os/map_data.py').read_text(encoding='utf-8'))
        zones = next(ast.literal_eval(n.value) for n in tree.body
                     if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict))
        for zone in zones.values():
            self.assertGreater(int(re.search(r'[0-9]+', zone['shape']).group()), 4)


if __name__ == '__main__':
    unittest.main()
