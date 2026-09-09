"""Scaled KR archive data-key text recognition without an emulator."""
import unittest
import cv2
import numpy as np
from module.handler.info_handler import kr_data_key_five_appear


class DataKeyPopupTest(unittest.TestCase):
    def test_scaled_five_key_label(self):
        source = cv2.cvtColor(cv2.imread('./assets/kr/handler/USE_DATA_KEY.png'), cv2.COLOR_BGR2RGB)
        label = cv2.resize(source[315:338, 604:734], None, fx=1.1, fy=1.1)
        image = np.zeros((720, 1280, 3), dtype=np.uint8)
        h, w = label.shape[:2]
        image[314:314+h, 600:600+w] = label
        self.assertTrue(kr_data_key_five_appear(image))

    def test_blank_not_confirmed(self):
        self.assertFalse(kr_data_key_five_appear(np.zeros((720, 1280, 3), dtype=np.uint8)))

    def test_unrelated_hard_fleet_asset_not_confirmed(self):
        image = cv2.cvtColor(cv2.imread('./assets/kr/map/FLEET_PREPARATION.png'), cv2.COLOR_BGR2RGB)
        self.assertFalse(kr_data_key_five_appear(image))


if __name__ == '__main__':
    unittest.main()
