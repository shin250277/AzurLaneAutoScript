"""Exact KR title variants must not weaken competing-identity rejection."""
import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class FinalReplayTitlesTest(unittest.TestCase):
    def test_three_observed_names_and_blank_negative(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            reader = KoreanIslandNameOcr([])
            for item, name in ((2704, '황광석'), (3034, '햄버그 덮밥'), (3115, '레몬 새우')):
                with self.subTest(item=item):
                    frame = load_image('assets/kr/island_item_name/%s_nov20_replay_selected.png' % item)
                    self.assertEqual(reader.ocr([frame], direct_ocr=True), [name])
                    self.assertEqual(reader.ocr([np.full_like(frame, 255)], direct_ocr=True), [''])
                    # A real different known title must remain that title.
                    other = load_image('assets/kr/island_item_name/3035_nov20_dispatch_selected.png')
                    self.assertEqual(reader.ocr([other], direct_ocr=True), ['천'])


if __name__ == '__main__':
    unittest.main()
