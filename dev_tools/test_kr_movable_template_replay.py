import unittest

import cv2
import numpy as np

from dev_tools.kr_movable_template_replay import search


class MovableSearchTest(unittest.TestCase):
    def test_displaced_patch_needs_full_colour_confirmation(self):
        rng = np.random.RandomState(11)
        sprite = cv2.resize(rng.randint(20, 195, (15, 19, 3)).astype(np.uint8),
                            (76, 60), interpolation=cv2.INTER_NEAREST)
        for delta, expected in ((0, True), (45, False)):
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            frame[303:363, 607:683] = sprite + delta
            preview = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (320, 180),
                                 interpolation=cv2.INTER_AREA)
            self.assertEqual(search(frame, preview, sprite), expected)
