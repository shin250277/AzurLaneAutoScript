"""Settlement and new-business controls share KR text but not positions."""
import subprocess
import sys
import unittest


class RestaurantReadyTest(unittest.TestCase):
    def test_settlement_is_not_new_business(self):
        import numpy as np
        from PIL import Image
        from module.base.button import Button
        receive = Button(area=(594, 611, 690, 641), color=(0, 0, 0),
                         button=(594, 611, 690, 641),
                         file='./assets/kr/island_handler/ISLAND_RESTAURANT_RECEIVE.png')
        start = Button(area=(713, 612, 810, 640), color=(0, 0, 0),
                       button=(713, 612, 810, 640),
                       file='./assets/kr/island_handler/ISLAND_RESTAURANT_START.png')
        with Image.open('dev_tools/fixtures/kr_restaurant_wide_start.png') as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(receive.match(frame, offset=(20, 20)))
        self.assertFalse(start.match(frame, offset=(20, 20)))
        self.assertFalse(receive.match(np.zeros_like(frame), offset=(20, 20)))
        with Image.open(start.file) as im:
            self.assertFalse(receive.match(np.array(im.convert('RGB')), offset=(20, 20)))

    def test_result_and_blank(self):
        import numpy as np
        from PIL import Image
        from module.base.button import Button
        result = Button(area=(261, 378, 354, 399), color=(0, 0, 0),
                        button=(261, 378, 354, 399),
                        file='./assets/kr/island_handler/ISLAND_RESTAURANT_RESULT.png')
        with Image.open('dev_tools/fixtures/kr_restaurant_result.png') as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(result.match(frame, offset=(20, 20)))
        self.assertFalse(result.match(np.zeros_like(frame), offset=(20, 20)))

    def test_staff_entry_unknown_is_bounded(self):
        code = '''
from unittest.mock import Mock, patch
from module.island_handler.restaurant import IslandRestaurant
from module.exception import RequestHumanTakeover
ui = Mock()
ui.config.SERVER = 'kr'
ui.unavailable_waitress_list.return_value = []
ui.loop.return_value = iter([])
with patch('module.island_handler.restaurant.get_waitress_slots', return_value=('any', 'none')):
    try:
        IslandRestaurant.choose_waitress(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Unknown staff entry must stop')
ui.loop.assert_called_once_with(timeout=10)
ui.device.image_save.assert_called_once()
ui.island_dock_find_character_with_blacklist.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_resting_control(self):
        import numpy as np
        from PIL import Image
        from module.base.button import Button
        resting = Button(area=(602, 611, 679, 641), color=(0, 0, 0),
                         button=(602, 611, 679, 641),
                         file='./assets/kr/island_handler/ISLAND_RESTAURANT_RESTING.png')
        with Image.open('dev_tools/fixtures/kr_restaurant_resting.png') as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(resting.match(frame, offset=(20, 20)))
        self.assertFalse(resting.match(np.zeros_like(frame), offset=(20, 20)))
        with Image.open('dev_tools/fixtures/kr_restaurant_wide_start.png') as im:
            self.assertFalse(resting.match(np.array(im.convert('RGB')), offset=(20, 20)))


if __name__ == '__main__':
    unittest.main()
