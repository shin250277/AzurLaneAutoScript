"""Strict whole-label masks must reject ambiguity, fragments and blank UI."""
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image


class NameMasksTest(unittest.TestCase):
    def references(self):
        return [(int(p.stem.split('_')[0]), np.array(Image.open(str(p)).convert('L')))
                for p in Path('assets/kr/island_item_name').glob('*.png')]

    def test_saved_flax_background_uses_existing_reference(self):
        from module.island_handler.korean_name_mask import mask_consensus
        frame = np.array(Image.open('dev_tools/fixtures/kr_flax_background.png').convert('L'))
        self.assertEqual(mask_consensus(frame, self.references()), 2010)

    def test_cross_label_leave_one_out_has_no_wrong_acceptance(self):
        from module.island_handler.korean_name_mask import mask_consensus
        refs = self.references()
        for i, (expected, frame) in enumerate(refs):
            with self.subTest(item=expected, reference=i):
                self.assertIn(mask_consensus(frame, refs[:i]+refs[i+1:]), (None, expected))

    def test_ambiguous_labels_blank_and_fragment_are_rejected(self):
        from module.island_handler.korean_name_mask import mask_consensus
        frame = np.array(Image.open('dev_tools/fixtures/kr_flax_background.png').convert('L'))
        self.assertIsNone(mask_consensus(frame, [(1, frame), (2, frame)]))
        self.assertIsNone(mask_consensus(np.full_like(frame, 255), self.references()))
        self.assertIsNone(mask_consensus(frame[:, :90], self.references()))
        self.assertIsNone(mask_consensus(frame[:, 120:], self.references()))
        doubled = np.concatenate((frame[:, 95:], frame[:, 95:]), axis=1)
        self.assertIsNone(mask_consensus(doubled, self.references()))
        decoration = np.full_like(frame, 255)
        decoration[20:22, 10:130] = 0
        self.assertIsNone(mask_consensus(decoration, self.references()))

    def test_unknown_backend_can_use_strict_masks_but_valid_conflict_cannot(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        frame = np.array(Image.open('dev_tools/fixtures/kr_flax_background.png').convert('RGB'))
        for read, expected in (([], '아마'), (['사과'], 'not-flax')):
            with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.return_value = [read]
                actual = KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True)
                if expected == 'not-flax':
                    self.assertNotEqual(actual, ['아마'])
                else:
                    self.assertEqual(actual, [expected])
