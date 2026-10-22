"""Optional local failure-frame replay; account screenshots never enter Git."""
from pathlib import Path
import unittest

import numpy as np
from PIL import Image
from module.base.button import Button
from module.combat.assets import BATTLE_STATUS_S


class StoredVictoryTest(unittest.TestCase):
    def test_stored_kr_victory_is_detected_by_actual_result_checker(self):
        path = Path('log/error/1790932553595/2026-10-02_18-15-53-511320.png')
        if not path.is_file():
            self.skipTest('Local KR failure frame unavailable; not a compatibility pass')
        button = Button(**{key: getattr(BATTLE_STATUS_S, 'raw_' + key)['kr']
                           for key in ('area', 'color', 'button', 'file')})
        with Image.open(str(path)) as im:
            frame = np.array(im.convert('RGB'))
        self.assertEqual(frame.shape, (720, 1280, 3))
        self.assertTrue(button.appear_on(frame, threshold=10))
        self.assertTrue(button.match(frame, offset=(0, 0), similarity=.85))
        x1, y1, x2, y2 = button.area
        frame[y1:y2, x1:x2] = 0
        self.assertFalse(button.appear_on(frame, threshold=10))
        self.assertFalse(button.match(frame, offset=(0, 0), similarity=.85))
