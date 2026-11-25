import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from dev_tools.extract_kr_fixed_labels_nov10 import CASES


class FixedLabelsTest(unittest.TestCase):
    def test_all_reviewed_fixed_recipe_labels_without_ocr_guessing(self):
        reader = KoreanIslandNameOcr([])
        for _, _, _, item_id, expected in CASES:
            with self.subTest(item_id=item_id), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda xs: [[] for _ in xs]
                frame = np.array(Image.open('dev_tools/fixtures/kr_fixed_nov10_%s.png' % item_id))
                self.assertEqual(reader.ocr([frame], direct_ocr=True), [expected])
                backend.assert_not_called()

    def test_blank_is_not_any_product(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda xs: [[] for _ in xs]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([np.full((31,146,3),255,np.uint8)], direct_ocr=True), [''])

    def test_clipped_omelet_still_requires_independent_icon_and_long_text(self):
        from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
        verifier = KoreanRecipeIconVerifier()
        frame = np.array(Image.open('dev_tools/fixtures/kr_omelet_icon_nov10.png'))
        self.assertEqual(verifier.confirm(frame, '끼운 당근 계란말0', {3033}), 3033)
        self.assertIsNone(verifier.confirm(frame, '', {3033}))
        self.assertIsNone(verifier.confirm(frame, '당근', {3033}))
        self.assertIsNone(verifier.confirm(frame, '햄버그 덮밥', {3033}))
        self.assertIsNone(verifier.confirm(frame, '끼운 당근 계란말0', {3034}))
