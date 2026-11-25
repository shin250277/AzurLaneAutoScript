import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped
from module.island.kr_season_claim import claimable_tasks


class SeasonClaimTest(unittest.TestCase):
    def tasks(self):
        return {1: {'target_num': 25, 'target': {3028: 25}},
                2: {'target_num': 5, 'target': {}},
                3: {'target_num': 10, 'target': {3028: 10}}}

    def test_preserves_restaurant_reserve(self):
        self.assertEqual(claimable_tasks({1: ('25/25', False)}, self.tasks(), {3028: 5}), [])
        self.assertEqual(claimable_tasks({1: ('30/25', False)}, self.tasks(), {3028: 5}), [1])

    def test_aggregates_all_ready_consumption(self):
        progress = {1: ('35/25', False), 3: ('35/10', False)}
        self.assertEqual(claimable_tasks(progress, self.tasks(), {3028: 5}), [])
        self.assertEqual(claimable_tasks(progress, self.tasks(), {}), [1, 3])

    def test_free_ready_and_obtained_are_distinct(self):
        self.assertEqual(claimable_tasks({2: ('5/5', False)}, self.tasks(), {}), [2])
        self.assertEqual(claimable_tasks({2: ('5/5', True)}, self.tasks(), {}), [])
        self.assertEqual(claimable_tasks({2: ('1/5', False)}, self.tasks(), {}), [])

    def test_invalid_evidence_is_not_permission(self):
        for progress in ({}, {9: ('5/5', False)}, {1: ('30/20', False)},
                         {1: ('?/25', False)}, {1: ('30/25', 1)},
                         {1: ('35/25', False), 3: ('40/10', False)}):
            self.assertIsNone(claimable_tasks(progress, self.tasks(), {}))
        self.assertIsNone(claimable_tasks({1: ('30/25', False)}, self.tasks(), {3028: -1}))

    def test_single_attempt_requires_two_obtained_confirmations(self):
        run = method('module/island/season_task.py', 'IslandSeasonTask',
                     'claim_korean_season_rewards', DIC_ISLAND_TASK=self.tasks(),
                     normalize_item_keys=lambda x: x, ISLAND_SEASON_TASK_RECEIVE_ALL='claim')
        for confirmed in (True, False):
            ui = SimpleNamespace(config=Mock(), device=Mock(),
                                 _kr_task_progress={2: ('5/5', False)},
                                 match_template_color=Mock(return_value=True),
                                 loop=lambda **kw: range(2), handle_island_additional=Mock())
            ui.config.cross_get.return_value = '{}'
            ui.audit_korean_season = Mock(side_effect=lambda **kw: setattr(
                ui, '_kr_task_progress', {2: ('5/5', confirmed)}))
            with patch('module.island.utils.load_hard_floor_items', return_value={}), patch(
                    'module.island_handler.restaurant_config.get_menu_reserve_items', return_value={}):
                if confirmed:
                    self.assertTrue(run(ui))
                    self.assertIsNone(ui.config.cross_set.call_args[0][1])
                else:
                    with self.assertRaises(TaskStopped):
                        run(ui)
                    self.assertEqual(ui.config.cross_set.call_count, 1)
            ui.device.click.assert_called_once_with('claim')
            self.assertEqual(ui.audit_korean_season.call_count, 2)

    def test_pending_attempt_blocks_before_scanning(self):
        run = method('module/island/season_task.py', 'IslandSeasonTask',
                     'sync_korean_season', current_season_task_ids=lambda: {2})
        ui = Mock()
        ui.config.cross_get.return_value = {'tasks': [2]}
        with self.assertRaises(TaskStopped):
            run(ui, claim=True)
        ui.audit_korean_season.assert_not_called()
        ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
