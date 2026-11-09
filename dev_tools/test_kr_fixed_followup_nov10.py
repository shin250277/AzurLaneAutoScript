"""Exact references must recognize only reviewed full public labels."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from dev_tools.extract_kr_fixed_followup_nov10 import CASES
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class FixedFollowupTest(unittest.TestCase):
    def test_reviewed_labels_without_ocr_guess(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            for _, _, _, item, name in CASES:
                with self.subTest(item=item):
                    frame = np.array(Image.open('dev_tools/fixtures/kr_fixed_followup_nov10_%s.png' % item))
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), [name])

    def test_blank_never_identifies_a_product(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([np.full((31,146,3),255,np.uint8)], direct_ocr=True), [''])
