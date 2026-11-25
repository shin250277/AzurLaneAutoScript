import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier


class IconContrastTest(unittest.TestCase):
    def read(self, votes, observed='', allowed=None, recognized=3049):
        icon=load_image('dev_tools/fixtures/kr_nov10_pair_notebook_3049_icon.png')
        label=load_image('dev_tools/fixtures/kr_nov10_pair_notebook_3049_name.png')
        verifier=KoreanRecipeIconVerifier()
        verifier.label_references=[]  # Isolate independent OCR, not glyph templates.
        with patch.object(verifier, 'match_item', return_value=recognized), patch(
                'module.ocr.windows_ocr.WindowsKoreanOcr') as ocr:
            ocr.return_value.atomic_ocr_for_single_lines.return_value=[list(v) for v in votes]
            result=verifier.confirm_visual(icon,label,observed,{3049} if allowed is None else allowed)
            return result,ocr.return_value.atomic_ocr_for_single_lines.call_count

    def test_three_exact_full_names_with_artwork(self):
        self.assertEqual(self.read(['수첩']*3)[0],3049)

    def test_bright_triplet_requires_all_three_and_no_known_conflict(self):
        icon=load_image('dev_tools/fixtures/kr_nov10_pair_notebook_3049_icon.png')
        label=load_image('dev_tools/fixtures/kr_nov10_pair_notebook_3049_name.png')
        verifier=KoreanRecipeIconVerifier()
        verifier.label_references=[]
        for first, last, expected in [
                (['?','',''], ['수첩']*3, 3049),
                (['?','',''], ['수첩','수첩',''], None),
                (['철광석','',''], ['수첩']*3, None)]:
            with patch.object(verifier,'match_item',return_value=3049), patch(
                    'module.ocr.windows_ocr.WindowsKoreanOcr') as ocr:
                ocr.return_value.atomic_ocr_for_single_lines.side_effect=[
                    [list(v) for v in first], [[],[],[]], [list(v) for v in last]]
                self.assertEqual(verifier.confirm_visual(icon,label,'',{3049}),expected)

    def test_no_partial_or_majority_or_transliteration(self):
        for votes in [[],['수첩']*2,['수첩','수첩',''],['수첩','수첩','수건'],
                      ['첩']*3,['수첩;']*3,['수첩A']*3]:
            self.assertIsNone(self.read(votes)[0])

    def test_no_artwork_never_requests_targeted_ocr(self):
        self.assertEqual(self.read(['수첩']*3,recognized=None),(None,0))

    def test_valid_conflicting_name_cannot_be_overridden(self):
        self.assertEqual(self.read(['수첩']*3,observed='철광석'),(None,0))

    def test_actual_artwork_must_match_allowed_product(self):
        icon=load_image('dev_tools/fixtures/kr_nov10_pair_notebook_3049_icon.png')
        verifier=KoreanRecipeIconVerifier()
        self.assertEqual(verifier.match_item(icon,{3049}),3049)
        self.assertIsNone(verifier.match_item(icon,{3038}))

    def test_tuna_artwork_and_exact_ocr_cannot_become_samchi(self):
        icon=load_image('dev_tools/fixtures/kr_nov10_pair_day_5103_icon.png')
        label=load_image('dev_tools/fixtures/kr_nov10_pair_day_5103_name.png')
        verifier=KoreanRecipeIconVerifier()
        verifier.label_references=[]
        with patch('module.ocr.windows_ocr.WindowsKoreanOcr') as ocr:
            ocr.return_value.atomic_ocr_for_single_lines.return_value=[list('참치')]*3
            self.assertEqual(verifier.confirm_visual(icon,label,'',{5103}),5103)
            self.assertIsNone(verifier.confirm_visual(icon,label,'삼치',{5103}))
            ocr.return_value.atomic_ocr_for_single_lines.return_value=[list('삼치')]*3
            self.assertIsNone(verifier.confirm_visual(icon,label,'',{5103}))
