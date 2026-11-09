import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class EveningLabelsTest(unittest.TestCase):
    def test_reviewed_public_names(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            for item, name in [(3114, '피시 앤 칩스'), (2605, '양모')]:
                with self.subTest(item=item):
                    frame = load_image('dev_tools/fixtures/kr_evening_%s.png' % item)
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), [name])
