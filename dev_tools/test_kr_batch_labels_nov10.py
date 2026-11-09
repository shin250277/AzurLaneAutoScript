import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from dev_tools.extract_kr_batch_labels_nov10 import CASES


class BatchLabelsTest(unittest.TestCase):
    def test_reviewed_labels_without_ocr_guess(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            for _, _, item, name in CASES:
                with self.subTest(item=item):
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([
                        load_image('dev_tools/fixtures/kr_batch_nov10_%s.png' % item)],
                        direct_ocr=True), [name])
