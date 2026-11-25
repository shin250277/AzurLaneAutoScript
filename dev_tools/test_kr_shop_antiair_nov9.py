import unittest
import numpy as np
from module.base.utils import load_image
from module.shop_event.korean_names import KoreanShopNames


class AntiairNameTest(unittest.TestCase):
    def test_observed_title_and_empty(self):
        reader = KoreanShopNames()
        frame = load_image('dev_tools/fixtures/kr_shop_antiair_nov9.png')
        self.assertEqual(reader.match(frame), 'PlateAntiairT3')
        self.assertIsNone(reader.match(np.full_like(frame, 200)))
