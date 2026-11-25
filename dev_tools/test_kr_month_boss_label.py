"""KR normal Arbiter title matching, without game interaction."""
import unittest

import numpy as np
from PIL import Image

from module.base.button import Button
from module.os_handler.assets import OS_MONTHBOSS_NORMAL


class KrMonthBossLabelTest(unittest.TestCase):
    def test_normal_title_shift_and_blank(self):
        button = Button(**{key: getattr(OS_MONTHBOSS_NORMAL, 'raw_' + key)['kr']
                           for key in ('area', 'color', 'button', 'file')})
        with Image.open(button.file) as image:
            frame = np.array(image.convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        shifted = np.zeros_like(frame)
        shifted[189:216, 572:716] = frame[184:211, 567:711]
        self.assertTrue(button.match(shifted, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))
        frame[184:211, 567:711] = 0
        self.assertFalse(frame.any(), 'Template must not contain account information')


if __name__ == '__main__':
    unittest.main()
