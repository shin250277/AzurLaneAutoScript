"""Button assets must retain screen coordinates and nonconstant template pixels."""
from pathlib import Path
import ast
import unittest
import cv2
import numpy as np
from PIL import Image


class MinigameAssetsTest(unittest.TestCase):
    def test_no_fixed_position_entrance_fallback(self):
        path = Path(__file__).resolve().parents[1] / 'module/minigame/new_year_challenge.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(n, ast.Name) and n.id == 'KR_NEW_YEAR_CHALLENGE_ENTRANCE'
                             for n in ast.walk(tree)))

    def test_templates_have_screen_coordinates_and_discriminating_pixels(self):
        root = Path(__file__).resolve().parents[1] / 'assets/kr/minigame'
        for name, area in [('START', (250, 418, 515, 498)),
                           ('END', (945, 557, 1083, 615))]:
            with self.subTest(name=name):
                with Image.open(str(root / ('NEW_YEAR_CHALLENGE_' + name + '.png'))) as image:
                    self.assertEqual(image.size, (1280, 720))
                    template = np.array(image.crop(area).convert('RGB'))
                self.assertGreater(float(template.std()), 10)
                blank = np.zeros((template.shape[0] + 10, template.shape[1] + 10, 3), dtype=np.uint8)
                self.assertLess(float(cv2.matchTemplate(blank, template, cv2.TM_CCOEFF_NORMED).max()), .85)
                self.assertGreater(float(cv2.matchTemplate(template, template, cv2.TM_CCOEFF_NORMED).max()), .99)


if __name__ == '__main__':
    unittest.main()
