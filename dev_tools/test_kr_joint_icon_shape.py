import unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
from module.island_handler.korean_name_mask import long_label_coverage_agrees

class JointIconShapeTest(unittest.TestCase):
    def test_orchard_exact_reference_and_conflict_guard(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        v = KoreanRecipeIconVerifier()
        label = load_image('dev_tools/fixtures/kr_nov10_orchard_name.png')
        icon = load_image('dev_tools/fixtures/kr_nov10_orchard_icon.png')
        self.assertEqual(KoreanIslandNameOcr([]).ocr([label], direct_ocr=True), ['감귤'])
        self.assertEqual(v.match_item(icon, {2017}), 2017)
        self.assertIsNone(v.confirm_visual(icon, label, '사과', {2017}))

    def test_charlotte_full_name_is_not_shortened_to_strawberry(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        label = load_image('dev_tools/fixtures/kr_nov10_charlotte_name.png')
        self.assertEqual(KoreanIslandNameOcr([]).ocr([label], direct_ocr=True), ['딸기 샬럿'])

    def test_dispatch_cloth_uses_reviewed_exact_reference(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        label = load_image('dev_tools/fixtures/kr_nov10_dispatch_cloth_name.png')
        self.assertEqual(KoreanIslandNameOcr([]).ocr([label], direct_ocr=True), ['천'])

    def test_bright_mango_requires_complete_three_level_group(self):
        v = KoreanRecipeIconVerifier()
        icon = load_image('dev_tools/fixtures/kr_nov10_joint_bright_mango_icon.png')
        label = load_image('dev_tools/fixtures/kr_nov10_joint_bright_mango_name.png')
        gray = cv2.cvtColor(label, cv2.COLOR_RGB2GRAY)
        self.assertFalse(long_label_coverage_agrees(gray, v.label_references,
            '망고 찹쌀밥', minimum_hangul=2, minimum_gap=.05))
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            self.assertEqual(v.confirm_visual(icon, label, '망고 잡쌀밥', {3025}), 3025)
            backend.assert_not_called()
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[], [], []]
            self.assertIsNone(v.confirm_visual(icon, label, '햄버그 덮밥', {3025}))
            with patch.object(v, 'complete_shape_agrees', return_value=False):
                self.assertIsNone(v.confirm_visual(icon, label, '', {3025}))

    def setUp(self):
        self.icon=load_image('dev_tools/fixtures/kr_nov10_joint_apple_icon.png')
        self.label=load_image('dev_tools/fixtures/kr_nov10_joint_apple_name.png')
        self.v=KoreanRecipeIconVerifier()

    def test_held_out_label_needs_all_independent_evidence(self):
        gray=cv2.cvtColor(self.label,cv2.COLOR_RGB2GRAY)
        self.assertFalse(long_label_coverage_agrees(gray,self.v.label_references,'애플파이',minimum_hangul=2))
        self.assertTrue(self.v.complete_shape_agrees(gray,'애플파이'))
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            self.assertEqual(self.v.confirm_visual(self.icon,self.label,'0H플파0Ü',{3009}),3009)
            backend.assert_not_called()

    def test_conflicts_blank_and_wrong_allowed_are_rejected(self):
        for label,observed,allowed in [(self.label,'오렌지 파이',{3009}),
                (np.full_like(self.label,255),'',{3009}),(self.label,'',{3025})]:
            with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.return_value=[[],[],[]]
                self.assertIsNone(self.v.confirm_visual(self.icon,label,observed,allowed))

    def test_wrong_grayscale_winner_cannot_relax_ink_margin(self):
        with patch.object(self.v,'complete_shape_agrees',return_value=False), patch(
                'module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value=[[],[],[]]
            self.assertIsNone(self.v.confirm_visual(self.icon,self.label,'',{3009}))

    def test_other_whole_labels_do_not_become_apple_from_icon(self):
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value=[[],[],[]]
            for path in sorted(Path('dev_tools/fixtures').glob('kr_nov10_pair_*_name.png')):
                if path.stem.endswith('_3009_name'):
                    continue
                with self.subTest(path=path.name):
                    self.assertIsNone(self.v.confirm_visual(self.icon,load_image(str(path)),'',{3009}))

    def test_short_rope_needs_shape_and_artwork_not_dilated_ink_alone(self):
        icon=load_image('dev_tools/fixtures/kr_nov10_joint_rope_icon.png')
        label=load_image('dev_tools/fixtures/kr_nov10_joint_rope_name.png')
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as backend:
            self.assertEqual(self.v.confirm_visual(icon,label,'~`스뇹',{3037}),3037)
            backend.assert_not_called()
            backend.return_value.atomic_ocr_for_single_lines.return_value=[[],[],[]]
            for path in sorted(Path('dev_tools/fixtures').glob('kr_nov10_pair_*_name.png')):
                if path.stem.endswith('_3037_name'):
                    continue
                with self.subTest(path=path.name):
                    self.assertIsNone(self.v.confirm_visual(icon,load_image(str(path)),'',{3037}))

    def test_cabinet_artwork_does_not_override_other_identity(self):
        icon=load_image('dev_tools/fixtures/kr_nov10_joint_cabinet_icon.png')
        label=load_image('dev_tools/fixtures/kr_nov10_joint_cabinet_name.png')
        self.assertEqual(self.v.match_item(icon,{3052}),3052)
        self.assertEqual(self.v.confirm_visual(icon,label,'',{3052}),3052)
        self.assertIsNone(self.v.confirm_visual(icon,label,'특선 나무통',{3052}))
        self.assertIsNone(self.v.confirm_visual(icon,label,'',{3051}))
