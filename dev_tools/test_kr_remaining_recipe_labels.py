import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class RemainingRecipeLabelsTest(unittest.TestCase):
    def test_reviewed_recipe_labels(self):
        for item, name in [(3114,'피시 앤 칩스'), (3103,'향기로운 과일 세트'),
                           (3025,'망고 찹쌀밥'), (3036,'가죽'), (3007,'라떼'), (3044,'못')]:
            with self.subTest(item=item):
                frame = np.array(Image.open('dev_tools/fixtures/kr_remaining_%s.png' % item))
                with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                    backend.return_value.atomic_ocr_for_single_lines.side_effect=lambda images:[[] for _ in images]
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame],direct_ocr=True),[name])
