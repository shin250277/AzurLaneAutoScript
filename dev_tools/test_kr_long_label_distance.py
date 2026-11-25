import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class LongLabelDistanceTest(unittest.TestCase):
    def test_short_partial_and_ambiguous_masks_rejected(self):
        import cv2
        from module.island_handler.korean_name_mask import long_label_coverage_agrees
        gray=cv2.cvtColor(np.array(Image.open('dev_tools/fixtures/kr_long_label_motion.png')),cv2.COLOR_RGB2GRAY)
        name='다진 고기 두부볶음'
        self.assertFalse(long_label_coverage_agrees(gray, [('두부',gray)], '두부'))
        self.assertFalse(long_label_coverage_agrees(gray, [(name,gray),('닭고기 감자 플래터',gray)], name))
        self.assertFalse(long_label_coverage_agrees(gray[:,:70], [(name,gray)], name))
        self.assertFalse(long_label_coverage_agrees(np.full_like(gray,255), [(name,gray)], name))

    def test_fractional_scroll_rendering(self):
        frame=np.array(Image.open('dev_tools/fixtures/kr_long_label_motion.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect=lambda images:[[] for _ in images]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame],direct_ocr=True),['다진 고기 두부볶음'])

    def test_other_valid_ocr_blocks_distance_candidate(self):
        frame=np.array(Image.open('dev_tools/fixtures/kr_long_label_motion.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value=[['두부']]
            self.assertNotEqual(KoreanIslandNameOcr([]).ocr([frame],direct_ocr=True),['다진 고기 두부볶음'])
