import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island.data import DIC_ISLAND_ITEM
from dev_tools.extract_kr_late_labels import CASES


class LateLabelsTest(unittest.TestCase):
    def test_reviewed_public_names(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            for _, _, _, item in CASES:
                name = DIC_ISLAND_ITEM[item]['name']['kr']
                with self.subTest(item=item):
                    frame = load_image('dev_tools/fixtures/kr_late_%s.png' % item)
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), [name])
