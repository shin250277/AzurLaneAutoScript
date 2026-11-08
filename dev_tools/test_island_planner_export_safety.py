"""Failed optimization must never erase an existing production configuration."""
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class PlannerExportSafetyTest(unittest.TestCase):
    def run_plan(self, export):
        calc = Mock(lp_success=False, lp_status=2)
        config = Mock()
        config.multi_set.side_effect = nullcontext
        ui = SimpleNamespace(current_activity_list=[], config=config,
                             create_calculator=Mock(return_value=calc),
                             RESTAURANT_MENU_CONFIG={})
        run = method('module/island_handler/production_planner.py',
                     'IslandProductionPlanner', 'run',
                     load_technology_status=lambda value: value,
                     load_hard_floor_items=lambda value: value)
        return run, ui, calc

    def test_unsolved_export_stops_before_any_write(self):
        run, ui, calc = self.run_plan(True)
        with self.assertRaises(TaskStopped):
            run(ui, tech_status_yaml={}, hard_floor_items_yaml={},
                task_target_items={}, stuck_season_order_id=0, export=True)
        ui.config.multi_set.assert_not_called()
        ui.config.cross_set.assert_not_called()
        calc.restaurant_menus_to_yaml.assert_not_called()

    def test_unsolved_read_only_analysis_remains_available(self):
        run, ui, calc = self.run_plan(False)
        self.assertIs(run(ui, tech_status_yaml={}, hard_floor_items_yaml={},
                          task_target_items={}, stuck_season_order_id=0, export=False), calc)
        ui.config.cross_set.assert_not_called()

    def test_success_exports_only_plan_fields_and_preserves_other_settings(self):
        run, ui, calc = self.run_plan(True)
        calc.lp_success = True
        calc.daily_buffer_items_to_yaml.return_value = 'buffer'
        calc.idle_accumulating_items_to_yaml.return_value = 'idle'
        calc.hard_floor_items_to_yaml.return_value = 'manual-floor'
        calc.restaurant_menus_to_yaml.return_value = {'one': 'menu'}
        ui.RESTAURANT_MENU_CONFIG = {'one': 'IslandBusiness.Menu'}
        run(ui, tech_status_yaml={'cached': True}, hard_floor_items_yaml={'wheat': 100},
            task_target_items={}, stuck_season_order_id=0, export=True)
        writes = dict(call[0] for call in ui.config.cross_set.call_args_list)
        self.assertEqual(writes, {
            'IslandProductionPlanner.Storage.Storage.IslandTechnologyStatus': {'cached': True},
            'IslandProduction.IslandProduction.DailyBufferItems': 'buffer',
            'IslandProduction.IslandProduction.IdleAccumulatingItems': 'idle',
            'IslandProduction.IslandProduction.HardFloorItems': 'manual-floor',
            'IslandBusiness.Menu': 'menu',
            'IslandProductionPlanner.IslandProductionPlanner.RescanIslandTechnology': False,
        })
        calc.solve_production_plan.assert_called_once_with(
            hard_floor_items={'wheat': 100}, task_target_items={}, stuck_season_order_id=0)

    def test_serialization_failure_does_not_partially_write_plan(self):
        run, ui, calc = self.run_plan(True)
        calc.lp_success = True
        calc.restaurant_menus_to_yaml.side_effect = ValueError('invalid plan')
        with self.assertRaises(ValueError):
            run(ui, tech_status_yaml={}, hard_floor_items_yaml={},
                task_target_items={}, stuck_season_order_id=0, export=True)
        ui.config.multi_set.assert_not_called()
        ui.config.cross_set.assert_not_called()

    def test_missing_restaurant_menu_stops_before_any_write(self):
        run, ui, calc = self.run_plan(True)
        calc.lp_success = True
        ui.RESTAURANT_MENU_CONFIG = {'one': 'IslandBusiness.Menu'}
        calc.restaurant_menus_to_yaml.return_value = {}
        with self.assertRaises((KeyError, TaskStopped)):
            run(ui, tech_status_yaml={}, hard_floor_items_yaml={},
                task_target_items={}, stuck_season_order_id=0, export=True)
        ui.config.multi_set.assert_not_called()
        ui.config.cross_set.assert_not_called()
