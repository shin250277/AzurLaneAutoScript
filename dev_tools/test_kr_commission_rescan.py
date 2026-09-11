"""Do not dispatch stale KR selections after a successful departure."""
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class CommissionRescanTest(unittest.TestCase):
    def setUp(self):
        self.run_start = method('module/commission/commission.py', 'RewardCommission',
                                '_commission_start_kr')
        self.ui = Mock()
        self.ui.daily_choose = []
        self.ui.urgent_choose = []

    def test_departure_discards_old_queue(self):
        first, stale, fresh = Mock(), Mock(), Mock()
        pages = [[first, stale], [fresh], []]
        def scan():
            self.ui.daily_choose = pages.pop(0)
        self.ui._commission_scan_all.side_effect = scan
        self.ui._commission_find_and_start.return_value = True
        self.run_start(self.ui)
        self.assertEqual([c[0][0] for c in self.ui._commission_find_and_start.call_args_list],
                         [first, fresh])
        stale.convert_to_running.assert_not_called()

    def test_failed_selection_is_not_success(self):
        target = Mock()
        self.ui.daily_choose = [target]
        self.ui._commission_find_and_start.return_value = False
        self.run_start(self.ui)
        self.ui._commission_scan_all.assert_called_once()
        target.convert_to_running.assert_not_called()

    def test_bounded_to_four_departures(self):
        self.ui.daily_choose = [Mock()]
        self.ui._commission_find_and_start.return_value = True
        self.run_start(self.ui)
        self.assertEqual(self.ui._commission_find_and_start.call_count, 4)


if __name__ == '__main__':
    unittest.main()
