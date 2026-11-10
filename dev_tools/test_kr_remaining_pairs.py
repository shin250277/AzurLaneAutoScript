import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
from dev_tools.extract_kr_remaining_pairs import SAMPLES


class RemainingPairsTest(unittest.TestCase):
    def test_reviewed_labels_without_windows_ocr(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            reader = KoreanIslandNameOcr([])
            for key, _, item in SAMPLES:
                with self.subTest(key=key, item=item):
                    frame = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_name.png' % (key,item))
                    self.assertEqual(reader.ocr([frame], direct_ocr=True), [DIC_ISLAND_ITEM[item]['name']['kr']])

    def test_artwork_never_authorizes_blank_or_conflicting_label(self):
        verifier = KoreanRecipeIconVerifier()
        for key, _, item in SAMPLES:
            with self.subTest(key=key, item=item):
                icon = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_icon.png' % (key,item))
                label = load_image('dev_tools/fixtures/kr_nov10_pair_%s_%s_name.png' % (key,item))
                self.assertIsNone(verifier.confirm_visual(icon, np.full_like(label,255), '', {item}))
                self.assertIsNone(verifier.confirm_visual(icon, label, '양모', {item}))
                self.assertIsNone(verifier.confirm_visual(icon, label, '', {999}))
