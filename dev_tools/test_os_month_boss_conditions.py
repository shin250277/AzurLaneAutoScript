"""Device-free month-boss precondition and result routing checks, not OCR tests."""
import unittest
from unittest.mock import Mock

import numpy as np

from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class MonthBossConditionsTest(unittest.TestCase):
    def setUp(self):
        self.ui = Mock()
        self.ui.config.task_stop.side_effect = TaskStopped
        self.ui.config.OpsiMonthBoss_Mode = 'normal'
        self.ui.config.OpsiMonthBoss_CheckAdaptability = True
        self.ui.is_in_opsi_explore.return_value = False
        self.ui.appear.side_effect = lambda button, **kw: button == 'normal'
        self.ui.get_adaptability.return_value = [203, 203, 156]
        self.ui.boss_clear.return_value = True
        self.reset = object()
        self.clear = method('module/os/tasks/month_boss.py', 'OpsiMonthBoss', 'clear_month_boss',
                            np=np, OS_MONTHBOSS_NORMAL='normal', OS_MONTHBOSS_HARD='hard',
                            get_os_next_reset=lambda: self.reset)

    def test_explore_schedule_stops_before_reading_boss(self):
        self.ui.is_in_opsi_explore.return_value = True
        with self.assertRaises(TaskStopped):
            self.clear(self.ui)
        self.ui.os_mission_enter.assert_not_called()
        self.ui.boss_clear.assert_not_called()

    def test_missing_boss_does_not_enter_combat(self):
        self.ui.appear.return_value = False
        self.ui.appear.side_effect = None
        self.clear(self.ui)
        self.ui.globe_goto.assert_not_called()
        self.ui.boss_clear.assert_not_called()
        self.ui.month_boss_delay.assert_called_once_with(is_normal=False, result=False)

    def test_normal_only_skips_hard_without_reporting_battle_success(self):
        self.ui.appear.side_effect = lambda button, **kw: button == 'hard'
        with self.assertRaises(TaskStopped):
            self.clear(self.ui)
        self.ui.boss_clear.assert_not_called()
        self.ui.month_boss_delay.assert_not_called()
        self.ui.config.task_delay.assert_called_once_with(target=self.reset)

    def test_any_low_adaptability_stops_before_travel(self):
        for values in ([202, 203, 156], [203, 202, 156], [203, 203, 155]):
            with self.subTest(values=values):
                self.ui.get_adaptability.return_value = values
                with self.assertRaises(TaskStopped):
                    self.clear(self.ui)
                self.ui.globe_goto.assert_not_called()
                self.ui.boss_clear.assert_not_called()

    def test_threshold_allows_combat_and_routes_actual_result(self):
        for result in (True, False):
            with self.subTest(result=result):
                self.ui.boss_clear.return_value = result
                self.clear(self.ui)
                self.ui.go_month_boss_room.assert_called_with(is_normal=True)
                self.ui.boss_clear.assert_called_with(has_fleet_step=True, is_month=True)
                self.ui.month_boss_delay.assert_called_with(is_normal=True, result=result)


if __name__ == '__main__':
    unittest.main()
