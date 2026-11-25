"""A weak runner-up permits reading, never acceptance without three OCR votes."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class ShortShapeConsensusTest(unittest.TestCase):
    def read(self, votes, initial=None):
        frame = np.array(Image.open('dev_tools/fixtures/kr_tuna_nov9_dispatch.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = (
                lambda frames: [initial or []] if len(frames) == 1 else votes)
            return KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True)

    def test_three_exact_readings_recover_real_dispatch_label(self):
        self.assertEqual(self.read([list('참치')]*3), ['참치'])

    def test_conflict_or_missing_vote_is_not_enough(self):
        for votes in ([list('참치'), [], list('참치')],
                      [list('참치'), list('삼치'), list('참치')], [],
                      [list('참치')]*2):
            with self.subTest(votes=votes):
                self.assertNotEqual(self.read(votes), ['참치'])

    def test_original_valid_other_name_is_not_overwritten(self):
        self.assertNotEqual(self.read([list('참치')]*3, list('삼치')), ['참치'])
