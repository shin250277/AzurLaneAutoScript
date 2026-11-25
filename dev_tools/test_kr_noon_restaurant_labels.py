import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from dev_tools.extract_kr_noon_restaurant_labels import LABELS
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class NoonRestaurantLabelsTest(unittest.TestCase):
    def test_complete_labels_without_ocr(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            for _, _, item, name, _ in LABELS:
                with self.subTest(item=item):
                    frame = np.array(Image.open('dev_tools/fixtures/kr_noon_restaurant_%s.png' % item))
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), [name])
