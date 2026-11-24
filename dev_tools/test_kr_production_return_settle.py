import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class ProductionReturnSettleTest(unittest.TestCase):
    def test_return_requires_stable_frames_and_invalidates_old_grids(self):
        timer = Mock()
        timer.start.return_value = timer
        timer.reached.side_effect = [False, False, True]
        invalidate = Mock()
        run = method('module/island/production.py', 'IslandProduction', 'settle_korean_dispatch_return',
                     Timer=Mock(return_value=timer), del_cached_property=invalidate,
                     page_island_manage=SimpleNamespace(check_button='manage'))
        ui = Mock()
        ui.loop.return_value = iter(range(3))
        ui.handle_island_additional.return_value = False
        ui.match_template_color.return_value = True
        ui.is_enter_window_shown.return_value = False
        self.assertTrue(run(ui))
        self.assertEqual(ui.match_template_color.call_count, 3)
        self.assertEqual([c[0][1] for c in invalidate.call_args_list],
                         ['production_grid', 'production_names', 'slot_grids'])
        ui.device.click.assert_not_called()

    def test_uncertain_return_stops_without_repeating_start(self):
        timer = Mock()
        timer.start.return_value = timer
        run = method('module/island/production.py', 'IslandProduction', 'settle_korean_dispatch_return',
                     Timer=Mock(return_value=timer), del_cached_property=Mock(),
                     page_island_manage=SimpleNamespace(check_button='manage'))
        ui = Mock()
        ui.loop.return_value = iter(range(3))
        ui.handle_island_additional.return_value = False
        ui.match_template_color.return_value = False
        with self.assertRaises(TaskStopped):
            run(ui)
        ui.device.click.assert_not_called()

    def test_dispatch_rechecks_slot_with_fresh_layout(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.kr_deferred_slots = set()
        ui.kr_verified_recipe_slots = {1}
        ui.slot_grids = {101: SimpleNamespace(buttons=['old'])}
        def invalidate(obj, key):
            if key == 'slot_grids':
                obj.slot_grids = {101: SimpleNamespace(buttons=['fresh'])}
        run = method('module/island/production.py', 'IslandProduction', 'dispatch_place',
                     DIC_ISLAND_PRODUCTION_PLACE={101: {'slot': [1]}}, production_place_name_with_id=str,
                     del_cached_property=invalidate, has_cached_property=lambda *a: False,
                     super=lambda: SimpleNamespace())
        ui.is_slot_empty.return_value = True
        run(ui, 101)
        ui.device.screenshot.assert_called_once()
        ui.is_slot_empty.assert_called_once_with('fresh')
        ui.dispatch_slot.assert_called_once_with(slot_id=1, slot_button='fresh')


if __name__ == '__main__':
    unittest.main()
