import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class SettledLabelsTest(unittest.TestCase):
    def test_public_labels_from_settled_failure_frames(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            ocr = KoreanIslandNameOcr([])
            for item in (2800, 2801, 2802, 3019, 3020, 3021, 3024, 3025, 3026, 3111, 3112, 3113):
                with self.subTest(item=item):
                    frame = load_image('dev_tools/fixtures/kr_settled_name_%s.png' % item)
                    self.assertEqual(ocr.ocr([frame], direct_ocr=True), [DIC_ISLAND_ITEM[item]['name']['kr']])
