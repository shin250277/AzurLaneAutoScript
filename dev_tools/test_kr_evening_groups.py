import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from dev_tools.extract_kr_evening_groups import CASES

class EveningGroupsTest(unittest.TestCase):
    def test_reviewed_names(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            ocr = KoreanIslandNameOcr([])
            for _, _, names in CASES:
                for name in names:
                    item = next(k for k,v in DIC_ISLAND_ITEM.items() if v['name'].get('kr') == name)
                    with self.subTest(item=item, name=name):
                        frame = load_image('dev_tools/fixtures/kr_evening_group_%s.png' % item)
                        self.assertEqual(ocr.ocr([frame], direct_ocr=True), [name])
