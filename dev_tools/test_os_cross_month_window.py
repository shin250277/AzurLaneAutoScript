"""Calendar guards without changing the host clock or invoking a game device."""
from datetime import datetime, timedelta
from unittest.mock import Mock
import unittest
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class CrossMonthWindowTest(unittest.TestCase):
    def test_far_or_invalid_reset_never_touches_game(self):
        now = datetime(2026, 10, 22, 10)
        for delta in (timedelta(days=4), timedelta(minutes=11), timedelta(seconds=-1)):
            ui = Mock()
            ui.os_cross_month_end.side_effect = TaskStopped
            run = method('module/os/tasks/cross_month.py', 'OpsiCrossMonth', 'os_cross_month',
                         datetime=Mock(now=Mock(return_value=now)), timedelta=timedelta,
                         get_os_next_reset=lambda: now + delta, ScriptError=ValueError)
            with self.assertRaises((TaskStopped, ValueError)):
                run(ui)
            ui.device.sleep.assert_not_called()
            ui.config.override.assert_not_called()
            ui.os_mission_overview_accept.assert_not_called()
            ui.storage_get_next_item.assert_not_called()
