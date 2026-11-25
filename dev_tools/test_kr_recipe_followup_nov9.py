import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier
from module.island_handler.korean_stock import KoreanRecipeStockDigit


class RecipeFollowupTest(unittest.TestCase):
    def test_fish_chips_public_label(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            frame = load_image('dev_tools/fixtures/kr_fish_chips_followup.png')
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['피시 앤 칩스'])

    def test_fruit_icon_requires_visible_long_text_and_correct_facility(self):
        frame = load_image('dev_tools/fixtures/kr_fruit_paradise_icon.png')
        verifier = KoreanRecipeIconVerifier()
        self.assertEqual(verifier.confirm(frame, '러풀 프루트 파라디', {3104}), 3104)
        self.assertIsNone(verifier.confirm(frame, '과일', {3104}))
        self.assertIsNone(verifier.confirm(frame, '러풀 프루트 파라디', {3034}))
        self.assertIsNone(verifier.confirm(frame, '향기로운 과일 세트', {3104}))

    def test_both_stock_positions_retain_final_one(self):
        ocr = KoreanRecipeStockDigit([], lang='cnocr', letter=(80,80,80), threshold=160)
        frames = [load_image('dev_tools/fixtures/kr_stock_61_%s.png' % suffix)
                  for suffix in ('previous', 'followup')]
        self.assertEqual(ocr.ocr(frames, direct_ocr=True), [61,61])
