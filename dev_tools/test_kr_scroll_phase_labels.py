from unittest.mock import patch
import unittest
from PIL import Image
import numpy as np
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr

class ScrollPhaseLabelsTest(unittest.TestCase):
    def test_reviewed_public_scroll_labels(self):
        for item in (4007,3014,3104,3108,3033,3034,3049,3044,3035,3010):
            with self.subTest(item=item), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.side_effect=lambda images:[[] for _ in images]
                frame=np.array(Image.open('dev_tools/fixtures/kr_scroll_phase_%s.png'%item))
                self.assertEqual(KoreanIslandNameOcr([]).ocr([frame],direct_ocr=True),
                                 [DIC_ISLAND_ITEM[item]['name']['kr']])
