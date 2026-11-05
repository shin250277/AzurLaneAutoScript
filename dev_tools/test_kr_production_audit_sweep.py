from unittest.mock import Mock
import unittest
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class ProductionAuditSweepTest(unittest.TestCase):
    def test_each_available_place_is_probed_once_without_production(self):
        run = method('module/island/production.py', 'IslandProduction', 'audit_korean_recipes',
                     DIC_ISLAND_PRODUCTION_PLACE={101: {'slot': [1]}, 201: {'slot': [2]}},
                     DIC_ISLAND_SLOT={i: {'formula': [i], 'activity_formula': []} for i in (1, 2)})
        ui = Mock()
        ui.slot_grids = {101: Mock(buttons=['a']), 201: Mock(buttons=['b'])}
        ui.is_slot_empty.return_value = True
        ui.next_page.return_value = False
        with self.assertRaises(TaskStopped):
            run(ui)
        self.assertEqual(ui.dispatch_slot.call_count, 2)
        for call in ui.dispatch_slot.call_args_list:
            self.assertTrue(call[1]['audit_only'])
        ui.dispatch_place.assert_not_called()
        ui.run_recipe.assert_not_called()
        ui.prepare_ingredients.assert_not_called()

    def test_busy_places_are_not_reassigned(self):
        run = method('module/island/production.py', 'IslandProduction', 'audit_korean_recipes',
                     DIC_ISLAND_PRODUCTION_PLACE={101: {'slot': [1]}},
                     DIC_ISLAND_SLOT={1: {'formula': [1], 'activity_formula': []}})
        ui = Mock()
        ui.slot_grids = {101: Mock(buttons=['a'])}
        ui.is_slot_empty.return_value = False
        ui.next_page.return_value = False
        with self.assertRaises(TaskStopped):
            run(ui)
        ui.dispatch_slot.assert_not_called()

    def test_distinct_ranch_recipes_are_not_skipped_or_duplicated(self):
        run = method('module/island/production.py', 'IslandProduction', 'audit_korean_recipes',
                     DIC_ISLAND_PRODUCTION_PLACE={102: {'slot': [1, 2, 3]}},
                     DIC_ISLAND_SLOT={
                         1: {'formula': [11], 'activity_formula': []},
                         2: {'formula': [12], 'activity_formula': []},
                         3: {'formula': [12], 'activity_formula': []}})
        ui = Mock()
        ui.slot_grids = {102: Mock(buttons=['a', 'b', 'c'])}
        ui.is_slot_empty.side_effect = lambda button: button != 'b'
        ui.next_page.return_value = False
        with self.assertRaises(TaskStopped):
            run(ui)
        self.assertEqual([call[0][0] for call in ui.dispatch_slot.call_args_list], [1, 3])
        self.assertTrue(all(call[1]['audit_only'] for call in ui.dispatch_slot.call_args_list))
