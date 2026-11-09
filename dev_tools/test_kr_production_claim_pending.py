import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from module.island.production import IslandProduction
from module.island.data import DIC_ISLAND_PRODUCTION_PLACE
from module.exception import RequestHumanTakeover


class PendingClaimTest(unittest.TestCase):
    def ui(self, result=True, finished=False, due=True, server='kr'):
        slot = DIC_ISLAND_PRODUCTION_PLACE[102]['slot'][0]
        stamp = datetime.now() + timedelta(days=-1 if due else 1)
        return slot, SimpleNamespace(
            config=SimpleNamespace(SERVER=server, cross_set=Mock()),
            slot_grids={102: SimpleNamespace(buttons=['slot'])},
            slot_finish_time={slot: stamp},
            is_slot_finished=Mock(return_value=finished),
            confirm_korean_empty_slot=Mock(return_value=False),
            claim_slot_reward=Mock(return_value=result))

    def test_stale_due_empty_slot_reconciles_without_claiming(self):
        slot, ui = self.ui(result=False)
        ui.confirm_korean_empty_slot.return_value = True
        ui.slot_finish_time[9999] = datetime.max
        IslandProduction.claim_reward_in_page(ui)
        self.assertEqual(ui.slot_finish_time, {9999: datetime.max})
        ui.claim_slot_reward.assert_not_called()
        ui.config.cross_set.assert_called_once_with(
            'IslandProduction.Storage.Storage.SlotFinishTime',
            {9999: datetime.max.isoformat(sep=' ')})

    def test_empty_confirmation_requires_all_observations(self):
        from dev_tools.test_os_task_stop_boundaries import method
        confirm = method('module/island/production.py', 'IslandProduction',
                         'confirm_korean_empty_slot', page_island_manage=SimpleNamespace())
        for empty, page, expected in (([True]*3, True, True),
                                      ([True, False], True, False),
                                      ([True]*3, False, False)):
            ui = SimpleNamespace(device=Mock(), ui_page_appear=Mock(return_value=page),
                                 is_enter_window_shown=Mock(return_value=False),
                                 is_slot_empty=Mock(side_effect=empty))
            self.assertEqual(confirm(ui, 'slot'), expected)
            ui.device.click.assert_not_called()

    def test_unconfirmed_due_reward_retains_timestamp_and_stops(self):
        for result in (False, None):
            slot, ui = self.ui(result=result)
            stamp = ui.slot_finish_time[slot]
            with self.assertRaises(RequestHumanTakeover):
                IslandProduction.claim_reward_in_page(ui)
            self.assertEqual(ui.slot_finish_time[slot], stamp)
            ui.claim_slot_reward.assert_called_once_with('slot')
            ui.config.cross_set.assert_not_called()

    def test_confirmed_reward_clears_only_completed_timestamp(self):
        slot, ui = self.ui()
        ui.slot_finish_time[9999] = datetime.max
        IslandProduction.claim_reward_in_page(ui)
        self.assertEqual(ui.slot_finish_time, {9999: datetime.max})
        ui.config.cross_set.assert_called_once_with(
            'IslandProduction.Storage.Storage.SlotFinishTime',
            {9999: datetime.max.isoformat(sep=' ')})

    def test_busy_not_due_slot_is_not_opened(self):
        slot, ui = self.ui(due=False)
        IslandProduction.claim_reward_in_page(ui)
        ui.claim_slot_reward.assert_not_called()
        self.assertIn(slot, ui.slot_finish_time)
        ui.config.cross_set.assert_not_called()

    def test_visual_completion_can_claim_before_estimated_time(self):
        slot, ui = self.ui(finished=True, due=False)
        IslandProduction.claim_reward_in_page(ui)
        self.assertNotIn(slot, ui.slot_finish_time)
        ui.config.cross_set.assert_called_once_with(
            'IslandProduction.Storage.Storage.SlotFinishTime', {})

    def test_foreign_server_existing_behavior_unchanged(self):
        slot, ui = self.ui(result=False, server='en')
        IslandProduction.claim_reward_in_page(ui)
        self.assertNotIn(slot, ui.slot_finish_time)
        ui.config.cross_set.assert_not_called()
