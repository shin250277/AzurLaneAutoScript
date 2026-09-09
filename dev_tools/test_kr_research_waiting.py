"""KR waiting labels must not fall back to Japanese text."""
import ast
from pathlib import Path
import unittest

import cv2
import numpy as np
from PIL import Image


class ResearchWaitingTest(unittest.TestCase):
    def test_waiting_template_is_registered_and_has_signal(self):
        tree = ast.parse(Path('module/research/assets.py').read_text(encoding='utf-8'))
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                          and n.targets[0].id == 'TEMPLATE_WAITING')
        files = ast.literal_eval(assignment.value.keywords[0].value)
        self.assertEqual(files['kr'], './assets/kr/research/TEMPLATE_WAITING.png')
        waiting = np.array(Image.open(files['kr']))
        self.assertEqual(waiting.ndim, 2)
        self.assertGreater(float(waiting.std()), 10)

    def test_waiting_does_not_match_detail(self):
        waiting = np.array(Image.open('assets/kr/research/TEMPLATE_WAITING.png'))
        detail = np.array(Image.open('assets/kr/research/TEMPLATE_DETAIL.png'))
        canvas = np.full((50, 220), 220, dtype=np.uint8)
        canvas[:detail.shape[0], :detail.shape[1]] = detail
        self.assertLess(float(cv2.matchTemplate(canvas, waiting, cv2.TM_CCOEFF_NORMED).max()), 0.75)


if __name__ == '__main__':
    unittest.main()
