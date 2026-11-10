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

    def test_without_independent_grayscale_insufficient_ink_stays_rejected(self):
        verifier = KoreanRecipeIconVerifier()
        for item in (3025, 3115):
            icon = load_image('dev_tools/fixtures/kr_late_%s_icon.png' % item)
            label = load_image('dev_tools/fixtures/kr_late_%s.png' % item)
            # Preserve the old ink-only rejection. The reviewed 3025 pair is a
            # correct complete name/artwork, not an adversarial wrong label;
            # the new independent grayscale evidence is tested separately.
            with patch.object(verifier,'complete_shape_agrees',return_value=False):
                self.assertIsNone(verifier.confirm_visual(icon, label, '', {item}))

    def test_reviewed_complete_mango_can_use_joint_evidence_not_other_name(self):
        verifier=KoreanRecipeIconVerifier()
        icon=load_image('dev_tools/fixtures/kr_late_3025_icon.png')
        label=load_image('dev_tools/fixtures/kr_late_3025.png')
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            self.assertEqual(verifier.confirm_visual(icon,label,'',{3025}),3025)
            backend.assert_not_called()
            self.assertIsNone(verifier.confirm_visual(icon,label,'오렌지 파이',{3025}))

    def test_other_product_label_cannot_borrow_correct_icon(self):
        verifier = KoreanRecipeIconVerifier()
        icon = load_image('dev_tools/fixtures/kr_late_3114_icon.png')
        label = load_image('dev_tools/fixtures/kr_late_3025.png')
        self.assertIsNone(verifier.confirm_visual(icon, label, '', {3114, 3025}))
