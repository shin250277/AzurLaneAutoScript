import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class AfternoonTitlesTest(unittest.TestCase):
    def test_exact_title_and_blank(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            reader = KoreanIslandNameOcr([])
            for item, name in ((3015, '야채 샐러드'), (3114, '피시 앤 칩스'), (3035, '천'), (3115, '레몬 새우'), (3023, '옥수수 컵')):
                frame = load_image('assets/kr/island_item_name/%s_nov20_afternoon_selected.png' % item)
                self.assertEqual(reader.ocr([frame], direct_ocr=True), [name])
                self.assertEqual(reader.ocr([np.full_like(frame,255)], direct_ocr=True), [''])


if __name__ == '__main__':
    unittest.main()
