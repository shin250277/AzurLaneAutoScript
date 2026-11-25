"""Conservative rejection of a fog boundary opposite a continuous outer edge."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

import numpy as np


class VerticalFogTest(unittest.TestCase):
    def recover(self, support=(.74, 1.), server='kr', task='OpsiDaily', span=701):
        path = Path('module/map_detection/homography.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == '_reject_kr_os_internal_vertical_edge')
        tree.body = [method]
        scope = dict(np=np, logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        image = np.zeros((1000, 1500), dtype=np.uint8)
        for x, ratio in zip((100, 100 + span), support):
            image[:int(1000 * ratio), x] = 255
        obj = SimpleNamespace(config=SimpleNamespace(SERVER=server,
                              Scheduler_Command=task, HOMO_TILE=(140, 140)),
                              left_edge=100, right_edge=100 + span,
                              lower_edge=None, upper_edge=None,
                              ui_mask_homo_stroke=np.full_like(image, 255))
        scope['_reject_kr_os_internal_vertical_edge'](obj, image)
        return obj

    def test_keeps_continuous_right_edge(self):
        obj = self.recover()
        self.assertIsNone(obj.left_edge)
        self.assertEqual(obj.right_edge, 801)

    def test_symmetric_left_edge(self):
        obj = self.recover(support=(1., .74))
        self.assertEqual(obj.left_edge, 100)
        self.assertIsNone(obj.right_edge)

    def test_does_not_guess_ambiguous_or_occluded_edges(self):
        for support in [(1., 1.), (.74, .74), (.74, .95), (.85, 1.)]:
            obj = self.recover(support=support)
            self.assertEqual((obj.left_edge, obj.right_edge), (100, 801))

    def test_preserves_other_regions_tasks_and_wide_maps(self):
        for kwargs in [dict(server='jp'), dict(task='Main'), dict(span=1120)]:
            obj = self.recover(**kwargs)
            self.assertIsNotNone(obj.left_edge)
            self.assertIsNotNone(obj.right_edge)

    def test_known_map_width_exceeds_short_pair(self):
        tree = ast.parse(Path('module/os/map_data.py').read_text(encoding='utf-8'))
        zones = next(ast.literal_eval(n.value) for n in tree.body
                     if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict))
        for zone in zones.values():
            self.assertGreater(ord(zone['shape'][0]) - ord('A') + 1, 6)


if __name__ == '__main__':
    unittest.main()
