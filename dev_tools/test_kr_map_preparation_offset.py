import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.map.assets import MAP_PREPARATION


class KrMapPreparationOffsetTest(unittest.TestCase):
    def test_expanded_dialog_tracks_shifted_shortcut(self):
        button = Button(area=MAP_PREPARATION.raw_area['kr'],
                        color=MAP_PREPARATION.raw_color['kr'],
                        button=MAP_PREPARATION.raw_button['kr'],
                        file=MAP_PREPARATION.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        shifted = np.zeros_like(frame)
        shifted[:, 56:] = frame[:, :-56]
        self.assertFalse(button.match(shifted, offset=(20, 20)))
        self.assertTrue(button.match(shifted, offset=(80, 20)))
        self.assertEqual(button.button[0], MAP_PREPARATION.raw_button['kr'][0] + 56)
        self.assertFalse(button.match(np.zeros_like(frame), offset=(80, 20)))
