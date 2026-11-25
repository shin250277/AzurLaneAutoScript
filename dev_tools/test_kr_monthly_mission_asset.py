"""KR daily missions must identify and skip the separate Arbiter mission."""
import ast
from pathlib import Path
import unittest

import cv2
import numpy as np
from PIL import Image


class MonthlyMissionAssetTest(unittest.TestCase):
    def test_generated_button_uses_korean_title(self):
        tree = ast.parse(Path('module/os_handler/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'MISSION_MONTHLY_BOSS')
        values = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(values['file']['kr'], './assets/kr/os_handler/MISSION_MONTHLY_BOSS.png')
        self.assertEqual(values['area']['kr'], (566, 186, 710, 207))

    def test_template_is_not_blank_and_keeps_screen_coordinates(self):
        path = Path('assets/kr/os_handler/MISSION_MONTHLY_BOSS.png')
        with Image.open(str(path)) as frame:
            self.assertEqual(frame.size, (1280, 720))
            template = np.array(frame.crop((566, 186, 710, 207)).convert('RGB'))
        self.assertGreater(float(template.std()), 10)
        blank = np.zeros((41, 164, 3), dtype=np.uint8)
        self.assertLess(float(cv2.matchTemplate(blank, template, cv2.TM_CCOEFF_NORMED).max()), .85)


if __name__ == '__main__':
    unittest.main()
