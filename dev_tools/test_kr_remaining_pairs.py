import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
from dev_tools.extract_kr_remaining_pairs import SAMPLES

ALL_SAMPLES = SAMPLES + [('mango', 1, 3025), ('gloves', 0, 3038), ('apple', 0, 3009), ('day', 1, 3120), ('day', 2, 2704), ('day', 1, 3035), ('day', 1, 3006)]
ALL_SAMPLES += [('evening',1,3025), ('evening',0,3048), ('evening',1,3007), ('evening',1,3014)]


class RemainingPairsTest(unittest.TestCase):
    def test_reviewed_labels_without_windows_ocr(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            reader = KoreanIslandNameOcr([])
            for key, _, item in ALL_SAMPLES:
                with self.subTest(key=key, item=item):
                    frame = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_name.png' % (key,item))
                    self.assertEqual(reader.ocr([frame], direct_ocr=True), [DIC_ISLAND_ITEM[item]['name']['kr']])

    def test_artwork_never_authorizes_blank_or_conflicting_label(self):
        verifier = KoreanRecipeIconVerifier()
        for key, _, item in ALL_SAMPLES:
            with self.subTest(key=key, item=item):
                icon = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_icon.png' % (key,item))
                label = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_name.png' % (key,item))
                self.assertIsNone(verifier.confirm_visual(icon, np.full_like(label,255), '', {item}))
                self.assertIsNone(verifier.confirm_visual(icon, label, '양모', {item}))
                self.assertIsNone(verifier.confirm_visual(icon, label, '', {999}))
