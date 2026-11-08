"""Collect independent read-only failures without ever admitting production."""
from unittest.mock import Mock
from types import SimpleNamespace
import unittest
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class UnknownName(Exception):
    pass


class AuditUnknownRecoveryTest(unittest.TestCase):
    def make(self):
        run = method('module/island/production.py', 'IslandProduction', 'audit_korean_recipes',
                     DIC_ISLAND_PRODUCTION_PLACE={101: {'slot': [1]}, 201: {'slot': [2]}},
                     DIC_ISLAND_SLOT={i: {'formula': [i], 'activity_formula': []} for i in (1, 2)},
                     KoreanRecipeNameUnknown=UnknownName,
                     page_island_manage=SimpleNamespace(check_button='manage'),
                     del_cached_property=Mock())
        ui = Mock()
        ui.slot_grids = {101: Mock(buttons=['a']), 201: Mock(buttons=['b'])}
        ui.is_slot_empty.return_value = True
        ui.is_in_recipe_menu.return_value = True
        ui.next_page.return_value = False
        return run, ui

    def test_unknown_name_is_saved_and_other_group_read_but_no_spending_allowed(self):
        run, ui = self.make()
        ui.dispatch_slot.side_effect = [UnknownName('unknown'), False]
        with self.assertRaisesRegex(TaskStopped, 'unresolved KR recipe groups'):
            run(ui)
        self.assertEqual(ui.dispatch_slot.call_count, 2)
        ui.device.image_save.assert_called_once_with('./log/kr_island_recipe_audit_101_1.png')
        ui.ui_back.assert_called_once_with(check_button='manage')
        ui.ui_ensure.assert_called_once()
        ui.run_recipe.assert_not_called()
        ui.dispatch_place.assert_not_called()

    def test_unknown_page_cannot_be_skipped(self):
        run, ui = self.make()
        ui.is_in_recipe_menu.return_value = False
        ui.dispatch_slot.side_effect = UnknownName('unknown')
        with self.assertRaises(UnknownName):
            run(ui)
        self.assertEqual(ui.dispatch_slot.call_count, 1)
        ui.ui_back.assert_not_called()

    def test_stock_or_other_safety_errors_still_stop_immediately(self):
        run, ui = self.make()
        ui.dispatch_slot.side_effect = TaskStopped('stock conflict')
        with self.assertRaisesRegex(TaskStopped, 'stock conflict'):
            run(ui)
        self.assertEqual(ui.dispatch_slot.call_count, 1)
        ui.ui_back.assert_not_called()
