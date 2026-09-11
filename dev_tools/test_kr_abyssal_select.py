import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.os.assets import SELECT_ABYSSAL, SELECT_OBSCURE


class KrAbyssalSelectTest(unittest.TestCase):
    def test_abyssal_label_is_localized(self):
        self.assertIn('kr', SELECT_ABYSSAL.raw_file)
        asset = SELECT_ABYSSAL
        button = Button(area=asset.raw_area['kr'], color=asset.raw_color['kr'],
                        button=asset.raw_button['kr'], file=asset.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 200), similarity=0.85))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 200), similarity=0.85))
        other = SELECT_OBSCURE
        other_frame = np.asarray(Image.open(other.raw_file['kr']).convert('RGB'))
        self.assertFalse(button.match(other_frame, offset=(20, 200), similarity=0.85))
        other_button = Button(area=other.raw_area['kr'], color=other.raw_color['kr'],
                              button=other.raw_button['kr'], file=other.raw_file['kr'])
        self.assertFalse(other_button.match(frame, offset=(20, 200), similarity=0.85))
