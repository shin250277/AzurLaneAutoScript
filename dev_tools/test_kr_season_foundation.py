import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island.korean_season_ocr import KoreanSeasonTaskOcr


class FoundationTitleTest(unittest.TestCase):
    def test_public_title_resolves_without_fuzzy_correction(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_season_foundation.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            self.assertEqual(KoreanSeasonTaskOcr([]).ocr([frame], direct_ocr=True), ['번영의 기반'])
