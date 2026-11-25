"""Offline daily-task progress and no-progress boundaries, not mission recognition."""
import unittest
from unittest.mock import Mock

from dev_tools.test_os_task_stop_boundaries import method


class OsDailyProgressTest(unittest.TestCase):
    def setUp(self):
        self.ui = Mock()
        self.ui.config.OpsiDaily_UseTuningSample = False
        self.ui.is_in_opsi_explore.return_value = False
        self.run = method('module/os/tasks/daily.py', 'OpsiDaily', 'os_daily')

    def test_all_accepted_and_empty_finishes_once(self):
        self.ui.os_mission_overview_accept.return_value = True
        self.ui.os_finish_daily_mission.return_value = 0
        self.run(self.ui)
        self.ui.os_mission_overview_accept.assert_called_once_with()
        self.ui.config.task_delay.assert_called_once_with(server_update=True)
        self.ui.tuning_sample_use.assert_not_called()
        self.ui.os_port_mission.assert_not_called()

    def test_two_no_progress_rounds_do_not_retry_forever(self):
        self.ui.os_mission_overview_accept.side_effect = [False, False]
        self.ui.os_finish_daily_mission.side_effect = [0, 0]
        self.run(self.ui)
        self.assertEqual(self.ui.os_finish_daily_mission.call_count, 2)
        self.ui.config.task_delay.assert_called_once_with(server_update=True)

    def test_completed_mission_resets_no_progress_counter(self):
        self.ui.os_mission_overview_accept.side_effect = [False] * 4
        self.ui.os_finish_daily_mission.side_effect = [0, 1, 0, 0]
        self.run(self.ui)
        self.assertEqual(self.ui.os_finish_daily_mission.call_count, 4)

    def test_explore_schedule_uses_port_path_and_returns(self):
        self.ui.os_mission_overview_accept.return_value = False
        self.ui.os_finish_daily_mission.return_value = 0
        self.ui.is_in_opsi_explore.return_value = True
        self.run(self.ui)
        self.ui.os_port_mission.assert_called_once_with()
        self.ui.os_mission_overview_accept.assert_called_once_with()

    def test_enabled_samples_are_used_once_not_per_retry(self):
        self.ui.config.OpsiDaily_UseTuningSample = True
        self.ui.os_mission_overview_accept.side_effect = [False, False]
        self.ui.os_finish_daily_mission.side_effect = [0, 0]
        self.run(self.ui)
        self.ui.tuning_sample_use.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
