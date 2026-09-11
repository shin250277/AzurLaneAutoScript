"""Capture ambiguous zero-HP readings without changing repair decisions."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class KrZeroHpDiagnosticTest(unittest.TestCase):
    def run_case(self, server='kr', hp=None, occupied=None, repair=None, saved=False,
                 recovered=None, blocked=False):
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER=server, OpsiGeneral_RepairThreshold=0.4),
            is_in_special_zone=Mock(return_value=False), hp_get=Mock(),
            hp=[0.0] * 6 if hp is None else hp,
            hp_has_ship=[True] * 6 if occupied is None else occupied,
            need_repair=[False] * 6 if repair is None else repair,
            device=Mock(), fleet_repair=Mock(), hp_reset=Mock(),
            _kr_zero_hp_saved=saved)
        run = method('module/os/map.py', 'OSMap', 'handle_fleet_repair')
        if recovered is not None:
            def reread():
                if ui.hp_get.call_count > 1:
                    ui.hp = recovered
            ui.hp_get.side_effect = reread
        if blocked:
            with self.assertRaises(TaskStopped):
                run(ui, revert=False)
            return ui, None
        result = run(ui, revert=False)
        return ui, result

    def test_ambiguous_zero_hp_saves_once_and_stops_before_unproven_repair(self):
        ui, result = self.run_case(blocked=True)
        ui.device.image_save.assert_called_once_with('./log/kr_os_zero_hp.png')
        self.assertTrue(ui._kr_zero_hp_saved)
        self.assertIsNone(result)
        ui.fleet_repair.assert_not_called()
        self.assertEqual(ui.device.screenshot.call_count, 3)
        ui.device.click.assert_not_called()
        ui, _ = self.run_case(saved=True, blocked=True)
        ui.device.image_save.assert_not_called()

    def test_transition_recovers_to_healthy_without_repair(self):
        ui, result = self.run_case(recovered=[0.98] * 6)
        self.assertFalse(result)
        ui.fleet_repair.assert_not_called()
        ui.device.screenshot.assert_called_once_with()

    def test_transition_recovers_to_actual_low_hp_and_keeps_threshold(self):
        ui, result = self.run_case(recovered=[0.2] + [0.98] * 5)
        self.assertTrue(result)
        ui.fleet_repair.assert_called_once_with(revert=False)

    def test_normal_empty_wrecked_and_other_server_do_not_capture(self):
        cases = [dict(hp=[0.98] * 6), dict(occupied=[False] * 6),
                 dict(repair=[True] + [False] * 5), dict(server='jp')]
        for case in cases:
            with self.subTest(case=case):
                ui, _ = self.run_case(**case)
                ui.device.image_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
