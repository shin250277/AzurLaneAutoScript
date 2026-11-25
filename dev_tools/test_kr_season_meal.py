import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island.korean_season_ocr import KoreanSeasonTaskOcr


class SeasonMealTest(unittest.TestCase):
    def test_observed_title_without_progress_digits(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_season_meal.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            self.assertEqual(KoreanSeasonTaskOcr([]).ocr([frame], direct_ocr=True), ['효율적인 식사'])

    def test_blank_title_is_not_a_task(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            self.assertEqual(KoreanSeasonTaskOcr([]).ocr([np.full((30, 241, 3), 255, dtype=np.uint8)], direct_ocr=True), [''])
