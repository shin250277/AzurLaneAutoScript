import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image


class ShapeConsensusTest(unittest.TestCase):
    def test_background_shape_requires_three_exact_ocr_votes(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        frame = np.array(Image.open('dev_tools/fixtures/kr_lavender_background.png'))
        for votes, accepted in (([['라벤더']]*3, True),
                                ([['라벤더'], ['라벤더'], []], False),
                                ([['라벤더'], ['당근'], ['라벤더']], False)):
            with self.subTest(votes=votes), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.side_effect = [[[]], votes]
                actual = KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True)
                self.assertEqual(actual == ['라벤더'], accepted)

    def test_valid_other_ocr_name_never_overwritten(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        frame = np.array(Image.open('dev_tools/fixtures/kr_lavender_background.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [['당근']]
            self.assertNotEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['라벤더'])
            backend.return_value.atomic_ocr_for_single_lines.assert_called_once()
