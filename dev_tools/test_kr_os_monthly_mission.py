"""Normal and hard Arbiter missions must both be excluded from KR dailies."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock

import numpy as np
from PIL import Image
from module.base.button import Button


class MonthlyMissionTest(unittest.TestCase):
    def load(self):
        tree = ast.parse(Path('module/os_handler/mission.py').read_text(encoding='utf-8'))
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'KR_MISSION_ARBITER'
                                  for t in n.targets))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'os_get_next_mission')
        tree.body = [assignment, method]
        scope = dict(Button=Button, logger=Mock(), MISSION_MONTHLY_BOSS='monthly',
                     MISSION_CHECKOUT='checkout')
        exec(compile(tree, 'mission.py', 'exec'), scope)
        return scope

    def test_shared_label_detects_normal(self):
        button = self.load()['KR_MISSION_ARBITER']
        frame = np.array(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(40, 20)))

    def test_shared_label_detects_shifted_hard_suffix(self):
        button = self.load()['KR_MISSION_ARBITER']
        source = np.array(Image.open(button.file).convert('RGB'))
        frame = np.zeros_like(source)
        frame[186:207, 675:730] = source[186:207, 655:710]
        self.assertTrue(button.match(frame, offset=(40, 20)))

    def test_blank_does_not_match(self):
        button = self.load()['KR_MISSION_ARBITER']
        self.assertFalse(button.match(np.zeros((720, 1280, 3), dtype=np.uint8), offset=(40, 20)))

    def test_kr_hard_boss_checks_only_following_mission(self):
        scope = self.load()
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.appear.side_effect = [False, True]
        ui.match_template_color.return_value = False
        self.assertFalse(scope['os_get_next_mission'](ui))
        ui.match_template_color.assert_called_once_with('checkout', offset=(-20, 100, 20, 150))
        ui.os_mission_quit.assert_called_once_with()
        ui.device.click.assert_not_called()

    def test_other_server_does_not_check_korean_label(self):
        scope = self.load()
        ui = Mock()
        ui.config.SERVER = 'jp'
        ui.appear.return_value = False
        ui.match_template_color.return_value = False
        scope['os_get_next_mission'](ui)
        ui.appear.assert_called_once_with('monthly', offset=(20, 20))
        ui.match_template_color.assert_called_once_with('checkout', offset=(20, 20))


if __name__ == '__main__':
    unittest.main()
