"""Only complete current-season evidence can become production reservations."""
import unittest
from unittest.mock import Mock
from types import SimpleNamespace
from dev_tools.test_kr_island_preflight import method

from module.island import kr_preflight


class SeasonTargetsTest(unittest.TestCase):
    def validate(self, ids, active=None, tasks=None):
        return kr_preflight.verified_season_targets(
            ids, {1, 2} if active is None else active,
            {1: {'target': {10: 2, 20: 3}}, 2: {'target': {10: 4}}} if tasks is None else tasks,
            {10: {}, 20: {}})

    def test_aggregates_all_targets_without_mutation(self):
        tasks = {1: {'target': {10: 2, 20: 3}}, 2: {'target': {10: 4}}}
        self.assertEqual(self.validate([1, 2], tasks=tasks), {10: 6, 20: 3})
        self.assertEqual(tasks[1]['target'], {10: 2, 20: 3})

    def test_empty_completed_scan_requires_known_active_season(self):
        self.assertEqual(self.validate([]), {})
        self.assertIsNone(self.validate([], active=set()))

    def test_invalid_task_evidence_is_not_a_partial_plan(self):
        for ids in (None, [None], [True], [1, 1], [1, 3], ['1']):
            with self.subTest(ids=ids):
                self.assertIsNone(self.validate(ids))

    def test_invalid_or_unknown_target_is_rejected(self):
        for target in (None, {10: True}, {10: -1}, {10: 0}, {10: 1.5}, {99: 1}):
            with self.subTest(target=target):
                self.assertIsNone(self.validate([1], tasks={1: {'target': target}}))
        self.assertIsNone(self.validate([1], tasks={}))


class SeasonSyncTest(unittest.TestCase):
    def runner(self):
        return method('module/island/season_task.py', 'sync_korean_season',
                      current_season_task_ids=lambda: {1, 2},
                      normalize_item_keys=lambda x: x, load_item_mapping=lambda x, **kw: x,
                      item_mapping_to_yaml=lambda x, **kw: x)

    def ui(self, results):
        return SimpleNamespace(config=Mock(), audit_korean_season=Mock(side_effect=results))

    def test_updates_only_target_after_two_agreeing_scans(self):
        ui = self.ui([{10: 6}, {10: 6}])
        ui.config.cross_get.return_value = {}
        self.runner()(ui)
        ui.config.cross_set.assert_called_once_with('IslandSeasonTask.IslandSeasonTask.TaskTarget', {10: 6})
        ui.config.task_delay.assert_called_once_with(server_update=True)
        self.assertEqual(ui.audit_korean_season.call_count, 2)

    def test_disagreement_or_exception_preserves_configuration(self):
        for results in ([{10: 6}, {}], [RuntimeError('unknown name')]):
            ui = self.ui(results)
            with self.assertRaises(RuntimeError):
                self.runner()(ui)
            ui.config.cross_set.assert_not_called()
            ui.config.task_delay.assert_not_called()

    def test_unchanged_target_does_not_rewrite_other_settings(self):
        ui = self.ui([{10: 6}, {10: 6}])
        ui.config.cross_get.return_value = {10: 6}
        self.runner()(ui)
        ui.config.cross_set.assert_not_called()

    def test_season_rollover_between_scans_blocks_write(self):
        runner = self.runner()
        runner.__globals__['current_season_task_ids'] = Mock(side_effect=[{1}, {2}])
        ui = self.ui([{}, {}])
        with self.assertRaises(RuntimeError):
            runner(ui)
        ui.config.cross_set.assert_not_called()


class VerifiedSeasonAuditTest(unittest.TestCase):
    def make(self, active):
        run = method('module/island/season_task.py', 'audit_korean_season',
                     current_season_task_ids=Mock(side_effect=active),
                     page_island_season='season', del_cached_property=Mock(),
                     verified_season_targets=kr_preflight.verified_season_targets,
                     DIC_ISLAND_TASK={1: {'target': {10: 2}}}, DIC_ISLAND_ITEM={10: {}})
        ui = Mock()
        ui.scan_all.return_value = [1]
        return run, ui

    def test_active_known_scan_returns_target_without_writing(self):
        run, ui = self.make([{1}, {1}])
        self.assertEqual(run(ui, return_verified=True), {10: 2})
        ui.config.cross_set.assert_not_called()
        ui.receive_all_reward.assert_not_called()

    def test_unknown_season_never_navigates(self):
        run, ui = self.make([set()])
        with self.assertRaisesRegex(RuntimeError, 'No verified active'):
            run(ui, return_verified=True)
        ui.ui_ensure.assert_not_called()
        ui.config.cross_set.assert_not_called()

    def test_rollover_or_unknown_task_rejects_candidate(self):
        for active, ids in (([{1}, {2}], [1]), ([{1}, {1}], [99])):
            run, ui = self.make(active)
            ui.scan_all.return_value = ids
            with self.assertRaisesRegex(RuntimeError, 'changed or invalid'):
                run(ui, return_verified=True)
            ui.config.cross_set.assert_not_called()


