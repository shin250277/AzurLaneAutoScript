import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class BuddhaNameTest(unittest.TestCase):
    def test_reviewed_scroll_label(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            frame = load_image('dev_tools/fixtures/kr_buddha_nov9.png')
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['불도장'])
