import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class HoneyScrollTest(unittest.TestCase):
    def test_reviewed_scroll_rendering_matches_without_ocr_guess(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_honey_scroll_nov9.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda xs: [[] for _ in xs]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['꿀 레몬 워터'])
            backend.assert_not_called()

    def test_blank_does_not_select_honey(self):
        frame = np.full((31,146,3),255,np.uint8)
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda xs: [[] for _ in xs]
            self.assertNotEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['꿀 레몬 워터'])
