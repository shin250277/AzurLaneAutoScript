import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.os_handler.assets import MISSION_FINISH


class KrOsMissionFinishTest(unittest.TestCase):
    def test_claim_label_is_localized(self):
        self.assertIn('kr', MISSION_FINISH.raw_file)
        button = Button(area=MISSION_FINISH.raw_area['kr'],
                        color=MISSION_FINISH.raw_color['kr'],
                        button=MISSION_FINISH.raw_button['kr'],
                        file=MISSION_FINISH.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))
