import unittest
from unittest.mock import patch
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
from module.island.data import DIC_ISLAND_ITEM
from pathlib import Path
import cv2


class VisualPairTest(unittest.TestCase):
    def test_full_label_and_independent_food_artwork(self):
        verifier = KoreanRecipeIconVerifier()
        # Do not prove a sample against its own newly captured exact reference.
        verifier.label_references = [(DIC_ISLAND_ITEM[int(p.stem.split('_')[0])]['name']['kr'],
                                      cv2.cvtColor(load_image(str(p)), cv2.COLOR_RGB2GRAY))
                                     for p in Path('assets/kr/island_item_name').glob('*.png')
                                     if '_late_' not in p.stem]
        for item in (3114,):
            icon = load_image('dev_tools/fixtures/kr_late_%s_icon.png' % item)
            label = load_image('dev_tools/fixtures/kr_late_%s.png' % item)
            with self.subTest(item=item):
                self.assertEqual(verifier.confirm_visual(icon, label, '', {item}), item)
                self.assertIsNone(verifier.confirm_visual(icon, label, '', {999}))
                self.assertIsNone(verifier.confirm_visual(icon, label, '양모', {item}))
                self.assertIsNone(verifier.confirm_visual(icon, np.full_like(label, 255), '', {item}))

    def test_insufficient_icon_or_competing_label_evidence_stays_rejected(self):
        verifier = KoreanRecipeIconVerifier()
        for item in (3025, 3115):
            icon = load_image('dev_tools/fixtures/kr_late_%s_icon.png' % item)
            label = load_image('dev_tools/fixtures/kr_late_%s.png' % item)
            self.assertIsNone(verifier.confirm_visual(icon, label, '', {item}))

    def test_other_product_label_cannot_borrow_correct_icon(self):
        verifier = KoreanRecipeIconVerifier()
        icon = load_image('dev_tools/fixtures/kr_late_3114_icon.png')
        label = load_image('dev_tools/fixtures/kr_late_3025.png')
        self.assertIsNone(verifier.confirm_visual(icon, label, '', {3114, 3025}))
