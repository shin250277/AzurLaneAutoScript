"""KR box-use template selection and negative-image regression."""
import unittest
import numpy as np
from module.base.button import Button
from module.storage.assets import BOX_USE, BOX_AMOUNT_CONFIRM, EQUIPMENT_FULL, DISASSEMBLE_CANCEL, DISASSEMBLE_CONFIRM, DISASSEMBLE_POPUP_CONFIRM


class KrBoxUseTest(unittest.TestCase):
    def test_disassemble_popup_uses_materials_header(self):
        self.assertIn('kr', DISASSEMBLE_POPUP_CONFIRM.raw_file)
        self.assertEqual(DISASSEMBLE_POPUP_CONFIRM.raw_area['kr'], (584, 173, 693, 195))
        from PIL import Image
        button = Button(area=DISASSEMBLE_POPUP_CONFIRM.raw_area['kr'],
                        color=DISASSEMBLE_POPUP_CONFIRM.raw_color['kr'],
                        button=DISASSEMBLE_POPUP_CONFIRM.raw_button['kr'],
                        file=DISASSEMBLE_POPUP_CONFIRM.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(-15, -5, 5, 70)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(-15, -5, 5, 70)))

    def test_disassemble_confirmation_has_korean_label(self):
        self.assertIn('kr', DISASSEMBLE_CONFIRM.raw_file)
        from PIL import Image
        button = Button(area=DISASSEMBLE_CONFIRM.raw_area['kr'],
                        color=DISASSEMBLE_CONFIRM.raw_color['kr'],
                        button=DISASSEMBLE_CONFIRM.raw_button['kr'],
                        file=DISASSEMBLE_CONFIRM.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))

    def test_disassemble_screen_has_korean_cancel_marker(self):
        self.assertIn('kr', DISASSEMBLE_CANCEL.raw_file)
        from PIL import Image
        button = Button(area=DISASSEMBLE_CANCEL.raw_area['kr'],
                        color=DISASSEMBLE_CANCEL.raw_color['kr'],
                        button=DISASSEMBLE_CANCEL.raw_button['kr'],
                        file=DISASSEMBLE_CANCEL.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))

    def test_full_storage_button_opens_organize_not_expansion(self):
        self.assertIn('kr', EQUIPMENT_FULL.raw_file)
        self.assertEqual(EQUIPMENT_FULL.raw_button['kr'], (413, 487, 569, 538))

    def test_amount_confirmation_has_korean_template(self):
        self.assertIn('kr', BOX_AMOUNT_CONFIRM.raw_file)
        from PIL import Image
        button = Button(area=BOX_AMOUNT_CONFIRM.raw_area['kr'],
                        color=BOX_AMOUNT_CONFIRM.raw_color['kr'],
                        button=BOX_AMOUNT_CONFIRM.raw_button['kr'],
                        file=BOX_AMOUNT_CONFIRM.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))

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
