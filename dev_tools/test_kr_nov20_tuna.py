import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class TunaLabelTest(unittest.TestCase):
    def test_reviewed_complete_title_without_guessing_blank(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            reader = KoreanIslandNameOcr([])
            for item, name in ((5103, '참치'), (4053, '물밤 케이크'), (4054, '설탕귤 찹쌀떡'),
                               (3051, '특선 나무통'), (3044, '못'), (4056, '겨울 꽃다발')):
                frame = load_image('assets/kr/island_item_name/%s_nov20_selected.png' % item)
                self.assertEqual(reader.ocr([frame], direct_ocr=True), [name])
                self.assertEqual(reader.ocr([np.full_like(frame, 255)], direct_ocr=True), [''])


if __name__ == '__main__':
    unittest.main()
