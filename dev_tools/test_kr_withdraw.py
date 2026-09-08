"""Offline localized withdrawal recognition, without device interaction."""
import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.map.assets import WITHDRAW


class WithdrawTest(unittest.TestCase):
    def test_localized_shifted_and_negative_frames(self):
        button = Button(**{k: getattr(WITHDRAW, 'raw_' + k)['kr']
                           for k in ('area', 'color', 'button', 'file')})
        with Image.open(button.file) as image:
            frame = np.array(image.convert('RGB'))
        self.assertTrue(button.match(frame, offset=(30, 30)))
        shifted = np.zeros_like(frame)
        shifted[658:711, 754:926] = frame[654:707, 749:921]
        self.assertTrue(button.match(shifted, offset=(30, 30)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(30, 30)))
        # A red rectangle alone must not be treated as the withdrawal button.
        blank_button = np.zeros_like(frame)
        blank_button[654:707, 749:921] = (209, 121, 121)
        self.assertFalse(button.match(blank_button, offset=(30, 30)))
        # The committed template must contain no account pixels outside its ROI.
        frame[654:707, 749:921] = 0
        self.assertFalse(frame.any())


if __name__ == '__main__':
    unittest.main()
