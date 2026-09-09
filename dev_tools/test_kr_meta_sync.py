"""Localized META synchronization label recognition."""
import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.meta_reward.assets import SYNC_TAP


class MetaSyncTest(unittest.TestCase):
    def test_label_shift_and_blank(self):
        b = Button(**{k: getattr(SYNC_TAP, 'raw_' + k)['kr']
                      for k in ('area', 'color', 'button', 'file')})
        with Image.open(b.file) as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(b.match(frame, offset=(20, 20)))
        shifted = np.zeros_like(frame)
        shifted[345:382, 569:725] = frame[340:377, 564:720]
        self.assertTrue(b.match(shifted, offset=(20, 20)))
        self.assertFalse(b.match(np.zeros_like(frame), offset=(20, 20)))
        frame[340:377, 564:720] = 0
        self.assertFalse(frame.any())


if __name__ == '__main__':
    unittest.main()
