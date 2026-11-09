import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class WorkshopSettledTest(unittest.TestCase):
    def test_reviewed_workshop_names(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            ocr = KoreanIslandNameOcr([])
            for item in (3043, 3044, 3049):
                with self.subTest(item=item):
                    frame = load_image('dev_tools/fixtures/kr_workshop_settled_%s.png' % item)
                    self.assertEqual(ocr.ocr([frame], direct_ocr=True), [DIC_ISLAND_ITEM[item]['name']['kr']])
