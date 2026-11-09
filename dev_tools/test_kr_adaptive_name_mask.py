import unittest
from unittest.mock import patch
import numpy as np
import cv2
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class AdaptiveNameMaskTest(unittest.TestCase):
    def frame(self, name):
        return np.array(Image.open('dev_tools/fixtures/kr_adaptive_%s.png' % name))

    def test_latte_lighting_without_new_reference_or_ocr_guess(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([self.frame('latte')], direct_ocr=True), ['라떼'])

    def test_adaptive_masks_reject_similar_fish_with_conflicting_levels(self):
        from module.island_handler.korean_name_mask import adaptive_mask_consensus
        gray = cv2.cvtColor(self.frame('tuna'), cv2.COLOR_RGB2GRAY)
        references = [(name, ref) for name, ref in KoreanIslandNameOcr([]).mask_references
                      if not np.array_equal(ref, gray)]
        self.assertIsNone(adaptive_mask_consensus(gray, references))

    def test_observed_tuna_exact_label_without_ocr_guess(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([self.frame('tuna')], direct_ocr=True), ['참치'])

    def test_valid_conflicting_name_is_not_replaced_by_latte(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [['가재'] for _ in frames]
            result = KoreanIslandNameOcr([]).ocr([self.frame('latte')], direct_ocr=True)
            self.assertNotEqual(result, ['라떼'])
