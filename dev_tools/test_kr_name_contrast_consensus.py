"""Noise is not a competing valid name; conflicting valid names always stop."""
import unittest
from module.island_handler.korean_ocr import confirmed_contrast_name


class ContrastConsensusTest(unittest.TestCase):
    def test_two_exact_readings_and_noise(self):
        self.assertTrue(confirmed_contrast_name('참치', ['참•치', '참치', '참치'], {'참치', '삼치'}))
        self.assertTrue(confirmed_contrast_name('참치', ['', '참치', '참치'], {'참치', '삼치'}))

    def test_competing_valid_name_is_not_outvoted(self):
        self.assertFalse(confirmed_contrast_name('참치', ['삼치', '참치', '참치'], {'참치', '삼치'}))

    def test_incomplete_single_or_wrong_evidence_is_rejected(self):
        for reads in [[], ['참치', '참치'], ['참치', '', ''], ['삼치'] * 3]:
            self.assertFalse(confirmed_contrast_name('참치', reads, {'참치', '삼치'}))
