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
