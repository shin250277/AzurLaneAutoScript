"""KR hard preparation must reject red stat restrictions before sortie."""
import ast
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np


class HardFleetStatsTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/map/map_fleet_preparation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_hard_stats_unsatisfied')]
        scope = {'np': np}
        exec(compile(tree, str(path), 'exec'), scope)
        self.detect = scope['_kr_hard_stats_unsatisfied']
        self.image = np.zeros((720, 1280, 3), dtype=np.uint8)

    def test_red_stat_rejected(self):
        self.image[553:563, 303:330] = (220, 60, 65)
        self.assertTrue(self.detect(self.image))

    def test_satisfied_yellow_allowed(self):
        self.image[553:563, 303:330] = (220, 200, 65)
        self.assertFalse(self.detect(self.image))

    def test_red_outside_stats_ignored(self):
        self.image[100:130, 1100:1190] = (220, 60, 65)
        self.assertFalse(self.detect(self.image))

    def test_sparse_noise_ignored(self):
        self.image[553, 303:323] = (220, 60, 65)
        self.assertFalse(self.detect(self.image))

    def preparation(self, red=False, fleet1=1, fleet2=2, visible=True):
        path = Path('module/map/map_fleet_preparation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'FleetPreparation')
        helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        tree.body = helpers + [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'fleet_preparation')]
        scope = dict(np=np, logger=Mock(),
                     FleetOperator=Mock(OFFSET=(20, 20),
                                        side_effect=AssertionError('Legacy fleet mutation path reached')),
                     AUTO_SEARCH_SET_MOB=Mock(), AUTO_SEARCH_SET_BOSS=Mock(),
                     AUTO_SEARCH_SET_ALL=Mock(), AUTO_SEARCH_SET_STANDBY=Mock(),
                     SUBMARINE_CLEAR='subclear',
                     FLEET_1_CLEAR='clear1', FLEET_1_CHOOSE='choose1',
                     FLEET_1_ADVICE='advice1', FLEET_1_BAR='bar1',
                     FLEET_1_IN_USE='in_use1', FLEET_1_HARD_SATIESFIED='satisfied1',
                     FLEET_2_CHOOSE='choose2', _kr_hard_stats_unsatisfied=self.detect,
                     HardNotSatisfied=ValueError)
        exec(compile(tree, str(path), 'exec'), scope)
        if visible:
            self.image[575:585, 130:230] = (220, 200, 65)
        if red:
            self.image[553:563, 303:330] = (220, 60, 65)
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr', Campaign_Mode='hard', Fleet_Fleet1=fleet1,
                                   Fleet_Fleet2=fleet2, Submarine_Fleet=0),
            map_fleet_checked=False, map_is_hard_mode=False,
            appear=Mock(side_effect=[True, False]), device=Mock(image=self.image))
        return scope['fleet_preparation'], ui

    def test_failed_stats_preserve_fleet_and_stop(self):
        prepare, ui = self.preparation(red=True)
        with self.assertRaises(ValueError):
            prepare(ui)
        self.assertFalse(ui.map_is_hard_mode)
        ui.device.click.assert_not_called()
        ui.device.screenshot.assert_called_once()
        ui.device.image_save.assert_called_once()

    def test_visible_stats_preserve_manual_fleet(self):
        prepare, ui = self.preparation(fleet2=0)
        self.assertFalse(prepare(ui))
        self.assertTrue(ui.map_is_hard_mode)
        ui.device.click.assert_not_called()

    def test_sp_normal_mode_constraint_screen_preserves_manual_fleet(self):
        prepare, ui = self.preparation()
        ui.config.Campaign_Mode = 'normal'
        self.assertFalse(prepare(ui))
        self.assertTrue(ui.map_is_hard_mode)
        ui.device.click.assert_not_called()

    def test_sp_normal_mode_unrecognized_constraints_stop_without_clearing(self):
        prepare, ui = self.preparation(visible=False)
        ui.config.Campaign_Mode = 'normal'
        with self.assertRaises(ValueError):
            prepare(ui)
        ui.device.click.assert_not_called()

    def test_real_dropdown_layout_keeps_legacy_selection_path(self):
        prepare, ui = self.preparation()
        ui.config.Campaign_Mode = 'normal'
        ui.appear.side_effect = lambda button, **kwargs: button in ('clear1', 'choose1')
        with self.assertRaisesRegex(AssertionError, 'Legacy fleet mutation path reached'):
            prepare(ui)
        ui.device.image_save.assert_not_called()

    def test_unrecognized_panel_stops_without_recommending(self):
        prepare, ui = self.preparation(visible=False)
        with self.assertRaises(ValueError):
            prepare(ui)
        ui.device.click.assert_not_called()
        self.assertFalse(ui.map_is_hard_mode)

    def test_already_checked_does_not_change_fleets(self):
        prepare, ui = self.preparation()
        ui.map_fleet_checked = True
        self.assertFalse(prepare(ui))
        ui.appear.assert_not_called()
        ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
