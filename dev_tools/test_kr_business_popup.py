import ast
from pathlib import Path
import subprocess
import sys
import unittest


class KoreanBusinessPopupTest(unittest.TestCase):
    def test_start_uses_korean_control_and_bounded_wait(self):
        tree = ast.parse(Path('module/island_handler/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'ISLAND_RESTAURANT_START')
        fields = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(fields['file']['kr'], './assets/kr/island_handler/ISLAND_RESTAURANT_START.png')
        code = '''
from unittest.mock import Mock
from module.island_handler.restaurant import IslandRestaurant
from module.exception import RequestHumanTakeover
ui = Mock()
ui.config.SERVER = 'kr'
ui.loop.return_value = iter([])
try:
    IslandRestaurant.restaurant_start(ui)
except RequestHumanTakeover:
    pass
else:
    raise AssertionError('Unknown start outcome accepted')
ui.loop.assert_called_once_with(timeout=15)
ui.device.image_save.assert_called_once()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_recommend_uses_korean_control(self):
        tree = ast.parse(Path('module/island_handler/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'ISLAND_RESTAURANT_RECOMMEND')
        fields = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(fields['file']['kr'], './assets/kr/island_handler/ISLAND_RESTAURANT_RECOMMEND.png')

    def test_unknown_revenue_screen_stops_with_bounded_diagnostic(self):
        code = '''
from unittest.mock import Mock
from module.island_handler.restaurant import IslandRestaurant
from module.exception import RequestHumanTakeover
ui = Mock()
ui.config.SERVER = 'kr'
ui.loop.return_value = iter([])
try:
    IslandRestaurant.receive_revenue(ui)
except RequestHumanTakeover:
    pass
else:
    raise AssertionError('Unknown revenue screen silently accepted')
ui.loop.assert_called_once_with(timeout=15)
ui.device.image_save.assert_called_once()
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_cancel_uses_korean_label(self):
        tree = ast.parse(Path('module/island/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'ISLAND_BUSINESS_EVENT_POPUP_CANCEL')
        fields = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(fields['file']['kr'], './assets/kr/island/ISLAND_BUSINESS_EVENT_POPUP_CANCEL.png')
        self.assertEqual(fields['area']['kr'], (479, 632, 552, 658))

    def test_navigation_is_rechecked_after_dismissing_popup(self):
        code = '''
from unittest.mock import Mock
from module.island.business import IslandBusiness
ui = Mock()
ui.config.SERVER = 'kr'
ui.is_in_island_restaurant.return_value = False
ui.appear.return_value = False
ui.island_manage_side_navbar_ensure.side_effect = [False, True]
ui.handle_restaurant_popup.return_value = True
ui.restaurant_swipe_to_top.side_effect = RuntimeError('scan reached')
try:
    IslandBusiness.run(ui)
except RuntimeError as exc:
    assert str(exc) == 'scan reached'
else:
    raise AssertionError('Expected scan sentinel')
assert ui.island_manage_side_navbar_ensure.call_count == 2
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
