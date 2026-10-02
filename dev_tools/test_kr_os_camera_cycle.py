"""Offline replay of alternating camera corrections; no device input."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np
from module.exception import RequestHumanTakeover


class CameraCycleTest(unittest.TestCase):
    def run_focus(self, positions, server='kr', task='OpsiDaily'):
        path = Path('module/map/camera.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'focus_to')
        tree.body = [method]
        scope = dict(np=np, logger=Mock(), location_ensure=lambda value: value,
                     location2node=str, RequestHumanTakeover=RequestHumanTakeover)
        exec(compile(tree, str(path), 'exec'), scope)
        obj = SimpleNamespace(camera=(12, 6), map=SimpleNamespace(shape=(19, 12)),
                              config=SimpleNamespace(SERVER=server, Scheduler_Command=task),
                              device=Mock())
        iterator = iter(positions)
        def swipe(vector):
            position = next(iterator, None)
            if position is None:
                return False
            obj.camera = position
            return True
        obj.map_swipe = Mock(side_effect=swipe)
        self.camera = obj
        scope['focus_to'](obj, (12, 6), swipe_limit=(6, 3))
        return obj

    def test_repeated_left_right_correction_stops_without_restart(self):
        with self.assertRaises(RequestHumanTakeover):
            self.run_focus([(1, 6), (18, 6)] * 8)
        self.assertEqual(self.camera.map_swipe.call_count, 6)

    def test_other_servers_and_normal_maps_keep_existing_behavior(self):
        for server, task in [('jp', 'OpsiDaily'), ('kr', 'Main')]:
            obj = self.run_focus([(1, 6), (18, 6)] * 4, server, task)
            self.assertEqual(obj.map_swipe.call_count, 9)

    def test_short_overshoot_may_recover(self):
        obj = self.run_focus([(1, 6), (18, 6), (1, 6), (18, 6), (12, 6)])
        self.assertEqual(obj.camera, (12, 6))

    def test_progress_is_not_a_cycle(self):
        self.run_focus([(x, 6) for x in range(1, 13)])

    def test_stationary_alignment_keeps_existing_protection(self):
        self.run_focus([(12, 6)] * 8)


if __name__ == '__main__':
    unittest.main()
