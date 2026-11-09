import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class ClothSettledTest(unittest.TestCase):
    def test_reviewed_single_glyph_with_settled_background(self):
        frame = load_image('dev_tools/fixtures/kr_cloth_settled.png')
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['천'])
