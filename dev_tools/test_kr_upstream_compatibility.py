"""Offline upstream merge gates: real color math and reproducible KR metadata."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import cv2
import numpy as np
from module.base.utils import color_mask, color_similarity_2d
from dev_tools.button_extract import ImageExtractor, ModuleExtractor
from dev_tools.test_os_task_stop_boundaries import method


class UpstreamCompatibilityTest(unittest.TestCase):
    def test_color_count_retains_previous_pixel_decisions(self):
        count = method('module/base/base.py', 'ModuleBase', 'image_color_count',
                       np=np, cv2=cv2, color_mask=color_mask)
        pixels = np.random.RandomState(31).randint(0, 256, (40, 60, 3), dtype=np.uint8)
        for color in [(254, 176, 54), (50, 184, 235), (0, 0, 0)]:
            for old in [200, 210, 220, 221, 230, 235, 245]:
                previous = cv2.countNonZero(cv2.inRange(color_similarity_2d(pixels, color), old, 255))
                for limit in [0, previous, max(0, previous - 1)]:
                    self.assertEqual(count(SimpleNamespace(), pixels, color, threshold=255-old, count=limit),
                                     previous > limit)

    def test_no_legacy_similarity_literals_remain(self):
        for path in Path('module').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                        and node.func.attr == 'image_color_count':
                    for key in node.keywords:
                        if key.arg == 'threshold' and isinstance(key.value, ast.Num):
                            self.assertLessEqual(key.value.n, 127, '{}:{}'.format(path, node.lineno))

    def test_generator_keeps_organize_not_premium_expansion(self):
        asset = ImageExtractor('storage', 'EQUIPMENT_FULL.png')
        self.assertEqual(asset.button['kr'], (413, 487, 569, 538))

    def test_generator_retains_custom_shop_confirmation(self):
        expressions = ModuleExtractor('os_shop').expression
        self.assertEqual(sum(line.startswith('SHOP_BUY_CONFIRM_INFO =') for line in expressions), 1)


if __name__ == '__main__':
    unittest.main()
