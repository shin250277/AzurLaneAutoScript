"""KR box-use template selection and negative-image regression."""
import unittest
import numpy as np
from module.base.button import Button
from module.storage.assets import BOX_USE


class KrBoxUseTest(unittest.TestCase):
    def test_kr_has_explicit_template(self):
        self.assertIn('kr', BOX_USE.raw_file)
        self.assertIn('kr', BOX_USE.raw_area)

    def test_template_matches_kr_label_not_blank(self):
        from PIL import Image
        button = Button(area=BOX_USE.raw_area['kr'],
                        color=BOX_USE.raw_color['kr'],
                        button=BOX_USE.raw_button['kr'],
                        file=BOX_USE.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))


if __name__ == '__main__':
    unittest.main()
