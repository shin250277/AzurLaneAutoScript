"""Bright labels still require whole-label identity and three exact votes."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from pathlib import Path
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class BrightShapeConsensusTest(unittest.TestCase):
    def read(self, bright, normal=None, initial='황광식'):
        frame = np.array(Image.open('dev_tools/fixtures/kr_bright_ore_nov10.png'))
        batches = iter([normal or ['?', '황광식', '황광석'], bright])
        def recognize(frames):
            return [list(initial)] if len(frames) == 1 else [list(v) for v in next(batches, [])]
        # Isolate the triple-OCR path: adaptive whole-label masks are tested
        # independently and may accept this exact observed shape without OCR.
        original_glob = Path.glob
        def without_new_exact_reference(path, pattern):
            # This regression deliberately exercises OCR fallback, not the
            # subsequently reviewed exact pixel reference of the same label.
            return (p for p in original_glob(path, pattern)
                    if p.name != '2704_noon_restaurant_selected.png')
        with patch.object(Path, 'glob', without_new_exact_reference), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend, patch(
                'module.island_handler.korean_name_mask.adaptive_mask_consensus', return_value=None):
            backend.return_value.atomic_ocr_for_single_lines.side_effect = recognize
            return KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True)

    def test_bright_three_exact_votes_recover_label(self):
        self.assertEqual(self.read(['황광석'] * 3), ['황광석'])

    def test_missing_or_conflicting_bright_votes_rejected(self):
        for votes in ([], ['황광석'] * 2, ['황광석', '', '황광석'],
                      ['황광석', '철광석', '황광석']):
            with self.subTest(votes=votes):
                self.assertNotEqual(self.read(votes), ['황광석'])

    def test_normal_known_conflict_cannot_be_overridden(self):
        self.assertNotEqual(self.read(['황광석'] * 3, ['철광석', '?', '황광석']), ['황광석'])

    def test_original_known_conflict_cannot_be_overridden(self):
        self.assertNotEqual(self.read(['황광석'] * 3, initial='철광석'), ['황광석'])

    def test_spaced_original_known_conflict_cannot_be_overridden(self):
        self.assertNotEqual(self.read(['황광석'] * 3, initial='철 광석'), ['황광석'])
