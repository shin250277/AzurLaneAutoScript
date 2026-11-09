import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandShopNameOcr


class WheatSeedShopLabelTest(unittest.TestCase):
    def test_wheat_seed_exact_label_without_ocr(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            label = np.array(Image.open('dev_tools/fixtures/kr_wheat_seed_shop.png'))
            self.assertEqual(KoreanIslandShopNameOcr([]).ocr([label], direct_ocr=True), ['밀 씨앗'])
