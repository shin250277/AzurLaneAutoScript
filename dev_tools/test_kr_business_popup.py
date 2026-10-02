import ast
from pathlib import Path
import subprocess
import sys
import unittest


class KoreanBusinessPopupTest(unittest.TestCase):
    def test_resting_list_rejects_active_start(self):
        import numpy as np
        from PIL import Image
        from module.base.template import Template
        template = Template('./assets/kr/island/TEMPLATE_ISLAND_BUSINESS_RESTING.png')
        with Image.open('dev_tools/fixtures/kr_business_resting_controls.png') as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(template.match(frame[526:562, 1004:1160]))
        self.assertFalse(template.match(frame[172:208, 1004:1160]))
        self.assertFalse(template.match(np.zeros((36, 156, 3), dtype=np.uint8)))

    def test_observed_running_rows_and_ready_row(self):
        import numpy as np
        from PIL import Image
        from module.base.template import Template
        template = Template('./assets/kr/island/TEMPLATE_ISLAND_BUSINESS_RUNNING.png')
        with Image.open('dev_tools/fixtures/kr_business_running_controls.png') as im:
            frame = np.array(im.convert('RGB'))
        for top in (252, 429, 606):
            self.assertTrue(template.match(frame[top:top + 36, 1004:1160]))
        self.assertFalse(template.match(frame[76:112, 1004:1160]))
        self.assertFalse(template.match(np.zeros((36, 156, 3), dtype=np.uint8)))

    def test_running_list_label_uses_korean_asset(self):
        tree = ast.parse(Path('module/island/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'TEMPLATE_ISLAND_BUSINESS_RUNNING')
        fields = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(fields['file']['kr'], './assets/kr/island/TEMPLATE_ISLAND_BUSINESS_RUNNING.png')

    def test_running_detected_inside_uses_remaining_time_not_midnight(self):
        code = '''
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from module.island.business import IslandBusiness
ui = object.__new__(IslandBusiness)
ui.config = Mock(SERVER='kr')
ui.device = Mock()
ui.skip_restaurant = {601: False, 602: False, 603: False, 604: False, 901: False}
for name in ('ui_back', 'ui_ensure', 'restaurant_swipe_to_top', 'next_restaurant'):
    setattr(ui, name, Mock())
ui.appear = Mock(return_value=False)
ui.is_in_island_restaurant = Mock(return_value=True)
ui.island_manage_side_navbar_ensure = Mock(return_value=True)
ui.handle_restaurant_popup = Mock(return_value=True)
ui.current_restaurant_button = Mock(return_value=Mock())
ui.get_restaurant_id = Mock(return_value=603)
ui.is_restaurant_running = Mock(return_value=False)
ui.is_restaurant_resting = Mock(return_value=False)
ui.restaurant_running = Mock(return_value=True)
ui.get_remain_time = Mock(return_value=timedelta(minutes=20))
ui.loop = Mock(side_effect=lambda **kwargs: iter([None]))
before = datetime.now()
with patch('module.island.business.RESTAURANT_IDS', [603]), \\
     patch('module.island_handler.restaurant.IslandRestaurant.run', return_value=False):
    ui.run()
target = ui.config.task_delay.call_args[1]['target']
assert before + timedelta(minutes=20) <= target <= datetime.now() + timedelta(minutes=20)
ui.get_remain_time.assert_called_once()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

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
