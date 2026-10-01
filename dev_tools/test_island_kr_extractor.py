import copy
import unittest
from datetime import datetime
from unittest.mock import patch, Mock

from dev_tools.island_kr_extractor import merge_entry, merge_time
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class IslandKrExtractorTest(unittest.TestCase):
    def test_unvalidated_korean_season_targets_stop_before_game_input(self):
        for file, cls in [('season_task', 'IslandSeasonTask')]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            run = method('module/island/{}.py'.format(file), cls, 'run',
                         page_island_order='order', page_island_season='season')
            with self.assertRaises(TaskStopped):
                run(ui)
            ui.ui_ensure.assert_not_called()

    def test_korean_orders_use_only_the_quota_verified_runner(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        run = method('module/island/order.py', 'IslandOrder', 'run')
        with patch('module.island.korean_order.run_regular_orders') as runner:
            run(ui)
            runner.assert_called_once_with(ui)
        ui.run_any_order.assert_not_called()

    def test_matching_numbers_add_only_korean_name(self):
        original = {'name': {'jp': 'JP'}, 'workload': 100}
        merged = copy.deepcopy(original)
        merge_entry(merged, {'name': {}, 'workload': 100}, '밀')
        self.assertEqual(merged, {'name': {'jp': 'JP', 'kr': '밀'}, 'workload': 100})
        self.assertEqual(original['name'], {'jp': 'JP'})

    def test_changed_numbers_fail_without_adding_name(self):
        row = {'name': {'jp': 'JP'}, 'workload': 100}
        with self.assertRaises(ValueError):
            merge_entry(row, {'workload': 200}, '밀')
        self.assertNotIn('kr', row['name'])

    def test_source_dates_are_not_copied_from_japan(self):
        row = {'start_time': {'jp': '2026-08-06 00:00:00'},
               'end_time': {'jp': '2026-11-05 00:00:00'}}
        merge_time(row, {0: {0: {0: 2026, 1: 8, 2: 20}, 1: {0: 0, 1: 0, 2: 0}},
                         1: {0: {0: 2026, 1: 11, 2: 19}, 1: {0: 12, 1: 0, 2: 0}}})
        self.assertEqual(row['end_time']['kr'], '2026-11-19 12:00:00')
        self.assertEqual(row['start_time']['jp'], '2026-08-06 00:00:00')

    def test_current_korean_season_uses_verified_activity_ids(self):
        import module.config.server as server
        from module.island_handler.production_plan_calculator import get_current_activity_list
        with patch.object(server, 'server', 'kr'):
            self.assertEqual(get_current_activity_list(datetime(2026, 9, 14)),
                             [990022, 990023, 990024, 990025])
            self.assertIsNone(get_current_activity_list(datetime(2026, 11, 19, 12)))
            self.assertEqual(get_current_activity_list(datetime(2026, 1, 1)), [])


if __name__ == '__main__':
    unittest.main()
