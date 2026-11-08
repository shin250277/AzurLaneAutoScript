"""A daily carousel must never be treated as the quick-battle selector."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
import subprocess
import sys
from unittest.mock import Mock


class DailyListGuardTest(unittest.TestCase):
    def test_observed_carousel_false_positive_requires_color(self):
        code = '''
import module.config.server as server
server.server = 'kr'
import numpy as np
from PIL import Image
from module.daily.daily import KR_DAILY_SKIP, KR_DAILY_NORMAL_RUN
from module.ui.assets import DAILY_CHECK
im = np.zeros((720,1280,3), dtype=np.uint8)
im[265:381,795:1005] = np.array(Image.open('dev_tools/fixtures/kr_daily_list_selector_negative.png'))
im[626:720,0:97] = np.array(Image.open('dev_tools/fixtures/kr_daily_list_info.png'))
KR_DAILY_SKIP.ensure_template()
KR_DAILY_NORMAL_RUN.ensure_template()
assert KR_DAILY_SKIP.image.std() > 10
assert KR_DAILY_NORMAL_RUN.image.std() > 10
assert not KR_DAILY_SKIP.match(im, offset=(20,20))
assert not KR_DAILY_SKIP.match_template_color(im, offset=(20,20))
assert DAILY_CHECK.match_template_color(im, offset=(30,30), threshold=15)
positive = np.zeros_like(im)
positive[295:351,825:975] = KR_DAILY_SKIP.image
positive[295:351,408:560] = KR_DAILY_NORMAL_RUN.image
assert KR_DAILY_SKIP.match_template_color(positive, offset=(20,20))
assert KR_DAILY_NORMAL_RUN.match_template_color(positive, offset=(20,20))
assert not DAILY_CHECK.match_template_color(positive, offset=(30,30), threshold=15)
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def setUp(self):
        tree = ast.parse(Path('module/daily/daily.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Daily')
        cls.bases = []
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'daily_enter']
        tree.body = [cls]
        scope = {'RequestHumanTakeover': RuntimeError, 'page_daily': object(),
                 'DAILY_ENTER_CHECK': object(), 'DAILY_CHECK': object()}
        exec(compile(tree, 'daily_guard', 'exec'), scope)
        self.daily = scope['Daily']()
        self.daily.config = SimpleNamespace(SERVER='kr')
        self.daily.device = Mock()
        self.daily.match_template_color = Mock(return_value=True)
        self.daily.appear = Mock(return_value=False)

    def test_unexpected_carousel_stops_before_any_selector_or_mission_click(self):
        with self.assertRaisesRegex(RuntimeError, 'before reward'):
            self.daily.daily_enter(object())
        self.daily.appear.assert_not_called()
        self.daily.device.click.assert_not_called()

    def test_reward_return_is_accepted_without_another_click(self):
        self.daily.match_template_color.side_effect = [False, True]
        self.daily.handle_get_items = Mock(return_value=True)
        self.assertFalse(self.daily.daily_enter(object()))
        self.assertTrue(self.daily._kr_daily_skip_returned)
        self.daily.device.click.assert_not_called()
        self.daily.device.screenshot.assert_called_once()

    def test_foreign_server_does_not_apply_kr_list_guard(self):
        self.daily.config.SERVER = 'jp'
        self.daily.appear.side_effect = ValueError('foreign path')
        with self.assertRaisesRegex(ValueError, 'foreign path'):
            self.daily.daily_enter(object())
        self.daily.match_template_color.assert_not_called()


if __name__ == '__main__':
    unittest.main()
