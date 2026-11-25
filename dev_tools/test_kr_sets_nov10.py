"""New restaurant labels keep the exact-reference and no-guess gates."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from dev_tools.extract_kr_sets_nov10 import CASES
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class RestaurantSetLabelsTest(unittest.TestCase):
    def test_blank_label_is_not_a_recipe(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            self.assertEqual(KoreanIslandNameOcr([]).ocr(
                [np.full((31, 146, 3), 220, dtype=np.uint8)], direct_ocr=True), [''])

    def test_labels_without_ocr_guess(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            for _, _, _, item, name in CASES:
                with self.subTest(item=item):
                    label = np.array(Image.open('dev_tools/fixtures/kr_sets_nov10_%s.png' % item))
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([label],direct_ocr=True), [name])
