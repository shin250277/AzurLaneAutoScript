import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class BottomFullLabelsTest(unittest.TestCase):
    def test_reviewed_bottom_labels(self):
        for item in (3114,3103,3104,3009,3033,3034,3117,3044,3046,3037,3010):
            with self.subTest(item=item):
                frame = np.array(Image.open('dev_tools/fixtures/kr_bottom_full_%s.png' % item))
                with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                    backend.return_value.atomic_ocr_for_single_lines.side_effect=lambda images:[[] for _ in images]
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame],direct_ocr=True),
                                     [DIC_ISLAND_ITEM[item]['name']['kr']])
