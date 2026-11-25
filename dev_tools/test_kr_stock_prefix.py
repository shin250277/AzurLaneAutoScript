import unittest
import cv2
import numpy as np
from module.island_handler.korean_stock import mask_stock_prefix


class StockPrefixTest(unittest.TestCase):
    def test_visible_colon_removes_prefix_only(self):
        image = np.full((18, 63), 255, dtype=np.uint8)
        image[1:16, :8] = 0  # Partial Korean label, not a number.
        image[6:9, 13:15] = 0
        image[14:16, 12:15] = 0
        cv2.putText(image, '0', (21, 15), cv2.FONT_HERSHEY_SIMPLEX, .5, 0, 1)
        original = image.copy()
        result = mask_stock_prefix(image)
        self.assertTrue(np.all(result[:, :15] == 255))
        np.testing.assert_array_equal(result[:, 15:], original[:, 15:])
        np.testing.assert_array_equal(image, original)

    def test_no_colon_never_drops_leading_digits(self):
        for value in ('0', '20', '52', '4722', '3792', '1111', '8888'):
            image = np.full((18, 63), 255, dtype=np.uint8)
            cv2.putText(image, value, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, .5, 0, 1)
            np.testing.assert_array_equal(mask_stock_prefix(image), image)

    def test_single_dot_and_blank_are_unchanged(self):
        image = np.full((18, 63), 255, dtype=np.uint8)
        np.testing.assert_array_equal(mask_stock_prefix(image), image)
        image[6:9, 13:15] = 0
        cv2.putText(image, '0', (21, 15), cv2.FONT_HERSHEY_SIMPLEX, .5, 0, 1)
        np.testing.assert_array_equal(mask_stock_prefix(image), image)
