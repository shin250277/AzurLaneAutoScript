import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr, punctuation_only_name


class PunctuationNameTest(unittest.TestCase):
    def read(self, value, votes):
        frame = load_image('dev_tools/fixtures/kr_cabbage_punctuation.png')
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: (
                [list(value)] if len(frames) == 1 else [list(v) for v in votes])
            return KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True)[0]

    def test_real_complete_shape_and_three_exact_votes(self):
        for value in ['배추 두부탕 !', '배추 두부탕 ,', '배추두부탕;']:
            self.assertEqual(self.read(value, ['배추 두부탕']*3), '배추 두부탕')

    def test_missing_or_conflicting_votes_are_not_authority(self):
        for votes in [[], ['배추 두부탕']*2, ['배추 두부탕','','배추 두부탕'],
                      ['배추 두부탕','철광석','배추 두부탕']]:
            self.assertNotEqual(self.read('배추 두부탕 ,', votes), '배추 두부탕')

    def test_other_letters_and_internal_punctuation_not_removed(self):
        for value in ['배추 두부탕A', '배추 두부탕2', '배추!두부탕', '두부탕!', '철광석!', '배추 두부탕?']:
            self.assertFalse(punctuation_only_name(value,'배추 두부탕'))

    def test_valid_competing_name_not_overridden(self):
        self.assertNotEqual(self.read('철광석', ['배추 두부탕']*3), '배추 두부탕')
