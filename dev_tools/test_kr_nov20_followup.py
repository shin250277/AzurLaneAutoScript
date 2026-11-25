import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class FollowupLabelsTest(unittest.TestCase):
    def test_complete_title_and_blank_rejection(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            reader = KoreanIslandNameOcr([])
            for item, name in ((2802, '엄선 목재'), (4049, '푸른 대추'), (4052, '푸른 대추죽'),
                               (3039, '향낭'), (3012, '다진 고기 두부볶음'), (3105, '태양의 꿀물'),
                               (3048, '종이'), (3043, '케이블'), (4056, '겨울 꽃다발'), (3028, '딸기 샬럿'),
                               (3046, '화약'), (3036, '가죽'), (2017, '감귤'), (3021, '라벤더 차'),
                               (3044, '못'), (3009, '애플파이'), (3035, '천')):
                suffix = '_selected' if item in (4056, 3035) else ''
                frame = load_image('assets/kr/island_item_name/%s_nov20_followup%s.png' % (item, suffix))
                self.assertEqual(reader.ocr([frame], direct_ocr=True), [name])
                self.assertEqual(reader.ocr([np.full_like(frame, 255)], direct_ocr=True), [''])


if __name__ == '__main__':
    unittest.main()
