"""Observed KR title classification, not a substitute for a Korean OCR model."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from module.commission import project


CASES = {
    'DAILY_RESOURCE_IV': 'daily_resource',
    'DAILY_RESOURCE_VI': 'daily_resource',
    'EXTRA_OIL_MEDIUM_I': 'extra_oil',
    'MAJOR_RESEARCH_ADVANCED': 'major_comm',
    'DAILY_CHIP_II': 'daily_chip',
    'DAILY_CHIP_II_SCROLL': 'daily_chip',
    'EXTRA_CUBE_LIVE_FIRE': 'extra_cube',
    'EXTRA_CUBE_LIVE_FIRE_SCROLL': 'extra_cube',
    'EXTRA_OIL_MEDIUM_III': 'extra_oil',
    'EXTRA_OIL_LARGE_III': 'extra_oil',
    'URGENT_DRILL_RECON': 'urgent_drill',
    'URGENT_BOX_NYB': 'urgent_box',
    'URGENT_PART_ISLAND': 'urgent_part',
    'URGENT_CUBE_ATTACK_II': 'urgent_cube',
    'URGENT_PART_ECOLOGY': 'urgent_part',
    'URGENT_PART_LOGISTICS': 'urgent_part',
}


class KoreanCommissionNamesTest(unittest.TestCase):
    def title(self, name):
        path = Path('assets/kr/commission/names') / (name + '.png')
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        self.assertIsNotNone(image, str(path))
        self.assertLessEqual(image.shape[0], 30)
        self.assertLessEqual(image.shape[1], 244)
        return image

    def test_observed_titles_classify_to_their_verified_genres(self):
        for name, genre in CASES.items():
            with self.subTest(name=name):
                self.assertEqual(project.classify_kr_name(self.title(name)), genre)

    def test_unknown_and_blank_names_are_not_guessed(self):
        self.assertEqual(project.classify_kr_name(None), '')
        self.assertEqual(project.classify_kr_name(np.full((19, 140), 255, dtype=np.uint8)), '')

    def test_conflicting_genres_are_not_guessed(self):
        title = self.title('DAILY_CHIP_II')
        with patch.object(project, '_kr_name_templates', return_value=[
                ('DAILY_CHIP_II', title), ('EXTRA_CUBE_LIVE_FIRE', title)]):
            self.assertEqual(project.classify_kr_name(title), '')

    def test_conflicting_names_of_same_genre_are_not_merged(self):
        title = self.title('DAILY_RESOURCE_IV')
        with patch.object(project, '_kr_name_templates', return_value=[
                ('DAILY_RESOURCE_IV', title), ('DAILY_RESOURCE_VI', title)]):
            self.assertEqual(project.classify_kr_name_key(title), '')

    def test_real_roman_order_and_medium_large_names_remain_distinct(self):
        for first, second in (
                ('DAILY_RESOURCE_IV', 'DAILY_RESOURCE_VI'),
                ('EXTRA_OIL_MEDIUM_I', 'EXTRA_OIL_MEDIUM_III'),
                ('EXTRA_OIL_MEDIUM_III', 'EXTRA_OIL_LARGE_III')):
            with self.subTest(first=first, second=second):
                a = SimpleNamespace(kr_name_image=self.title(first))
                b = SimpleNamespace(kr_name_image=self.title(second))
                self.assertFalse(project.Commission.kr_name_match(a, b))


if __name__ == '__main__':
    unittest.main()
