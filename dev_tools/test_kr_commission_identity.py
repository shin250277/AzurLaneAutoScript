"""KR fallback commissions must keep their full visual name identity."""
import copy
from datetime import timedelta
import unittest

import cv2
import numpy as np

from module.commission import project


class KoreanCommissionIdentityTest(unittest.TestCase):
    def name_image(self, title, dx=0, dy=0):
        image = np.full((40, 260, 3), 75, dtype=np.uint8)
        cv2.putText(image, title, (12 + dx, 26 + dy), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (220, 220, 220), 1, cv2.LINE_AA)
        return project.crop_kr_name_image(image, (0, 0, 260, 40))

    def commission(self, title):
        comm = project.Commission.__new__(project.Commission)
        comm.valid = True
        comm.genre, comm.category_str = 'urgent_drill', 'urgent'
        comm.status = 'pending'
        comm.duration = timedelta(hours=4)
        comm.expire = timedelta(hours=2)
        comm.repeat_count = 1
        comm.kr_name_image = self.name_image(title)
        return comm

    def test_matching_name_survives_position_and_countdown_change(self):
        first = self.commission('OIL FIELD I')
        second = copy.deepcopy(first)
        second.kr_name_image = self.name_image('OIL FIELD I', dx=5, dy=2)
        second.expire -= timedelta(seconds=10)
        self.assertEqual(first, second)

    def test_same_time_different_name_or_roman_suffix_is_not_same_commission(self):
        first = self.commission('OIL FIELD I')
        for title in ('OIL FIELD III', 'CARGO RUN I'):
            with self.subTest(title=title):
                self.assertNotEqual(first, self.commission(title))

    def test_unreadable_name_does_not_match_even_with_same_timing(self):
        first = self.commission('OIL FIELD I')
        second = copy.deepcopy(first)
        second.kr_name_image = None
        self.assertNotEqual(first, second)
        first.kr_name_image = None
        self.assertNotEqual(first, second)

    def test_blank_crop_is_not_a_name(self):
        self.assertIsNone(project.crop_kr_name_image(
            np.full((40, 260, 3), 75, dtype=np.uint8), (0, 0, 260, 40)))

    def observed(self, title):
        comm = self.commission('placeholder')
        comm.kr_name_image = cv2.imread('assets/kr/commission/names/' + title + '.png', 0)
        comm.kr_name_key = project.classify_kr_name_key(comm.kr_name_image)
        comm.name = title
        comm.genre = project.classify_kr_name(comm.kr_name_image)
        comm.category_str = comm.genre.split('_', 1)[0]
        comm.suffix_image = None
        return comm

    def test_observed_scroll_variants_share_name_identity(self):
        for title in ('DAILY_CHIP_II', 'EXTRA_CUBE_LIVE_FIRE', 'EXTRA_CUBE_FLEET_ESCORT'):
            with self.subTest(title=title):
                self.assertEqual(self.observed(title), self.observed(title + '_SCROLL'))

    def test_fleet_escort_is_not_live_fire_despite_same_cube_reward(self):
        self.assertNotEqual(self.observed('EXTRA_CUBE_FLEET_ESCORT'),
                            self.observed('EXTRA_CUBE_LIVE_FIRE'))

    def test_full_korean_title_is_not_vetoed_by_legacy_suffix_crop(self):
        first = self.observed('DAILY_RESOURCE_IV')
        second = copy.deepcopy(first)
        second.suffix_image = np.zeros((20, 20), dtype=np.uint8)
        self.assertEqual(first, second)

    def test_known_genre_does_not_merge_distinct_roman_names(self):
        self.assertNotEqual(self.observed('DAILY_RESOURCE_IV'), self.observed('DAILY_RESOURCE_VI'))

    def test_cached_name_key_cannot_replace_missing_image(self):
        first = self.observed('DAILY_RESOURCE_IV')
        second = copy.deepcopy(first)
        second.kr_name_image = None
        self.assertNotEqual(first, second)

    def test_equal_render_variants_have_equal_hashes(self):
        first = self.observed('DAILY_CHIP_II')
        second = self.observed('DAILY_CHIP_II_SCROLL')
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))


if __name__ == '__main__':
    unittest.main()
