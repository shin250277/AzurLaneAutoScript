"""KR hard preparation must reject red stat restrictions before sortie."""
import ast
from pathlib import Path
import unittest
import numpy as np


class HardFleetStatsTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/map/map_fleet_preparation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_hard_stats_unsatisfied')]
        scope = {'np': np}
        exec(compile(tree, str(path), 'exec'), scope)
        self.detect = scope['_kr_hard_stats_unsatisfied']
        self.image = np.zeros((720, 1280, 3), dtype=np.uint8)

    def test_red_stat_rejected(self):
        self.image[553:563, 303:330] = (220, 60, 65)
        self.assertTrue(self.detect(self.image))

    def test_satisfied_yellow_allowed(self):
        self.image[553:563, 303:330] = (220, 200, 65)
        self.assertFalse(self.detect(self.image))

    def test_red_outside_stats_ignored(self):
        self.image[100:130, 1100:1190] = (220, 60, 65)
        self.assertFalse(self.detect(self.image))

    def test_sparse_noise_ignored(self):
        self.image[553, 303:323] = (220, 60, 65)
        self.assertFalse(self.detect(self.image))


if __name__ == '__main__':
    unittest.main()
