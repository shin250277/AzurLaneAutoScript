"""Capture ambiguous zero-HP readings without changing repair decisions."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from dev_tools.test_os_task_stop_boundaries import method


class KrZeroHpDiagnosticTest(unittest.TestCase):
    def run_case(self, server='kr', hp=None, occupied=None, repair=None, saved=False):
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER=server, OpsiGeneral_RepairThreshold=0.4),
            is_in_special_zone=Mock(return_value=False), hp_get=Mock(),
            hp=[0.0] * 6 if hp is None else hp,
            hp_has_ship=[True] * 6 if occupied is None else occupied,
            need_repair=[False] * 6 if repair is None else repair,
            device=Mock(), fleet_repair=Mock(), hp_reset=Mock(),
            _kr_zero_hp_saved=saved)
        run = method('module/os/map.py', 'OSMap', 'handle_fleet_repair')
        result = run(ui, revert=False)
        return ui, result

    def test_ambiguous_zero_hp_saves_current_frame_once_and_keeps_repair(self):
        ui, result = self.run_case()
        ui.device.image_save.assert_called_once_with('./log/kr_os_zero_hp.png')
        self.assertTrue(ui._kr_zero_hp_saved)
        self.assertTrue(result)
        ui.fleet_repair.assert_called_once_with(revert=False)
        ui.device.screenshot.assert_not_called()
        ui.device.click.assert_not_called()
        ui, _ = self.run_case(saved=True)
        ui.device.image_save.assert_not_called()

    def test_normal_empty_wrecked_and_other_server_do_not_capture(self):
        cases = [dict(hp=[0.98] * 6), dict(occupied=[False] * 6),
                 dict(repair=[True] + [False] * 5), dict(server='jp')]
        for case in cases:
            with self.subTest(case=case):
                ui, _ = self.run_case(**case)
                ui.device.image_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
