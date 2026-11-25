import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class MilkshakeLabelTest(unittest.TestCase):
    def test_unknown_ocr_is_not_confused_with_other_cafe_items(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_milkshake_label.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [['딸기 일크쉐이크'] for _ in images]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['딸기 밀크쉐이크'])
