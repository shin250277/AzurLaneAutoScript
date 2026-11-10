import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class UnknownName(Exception):
    pass


class DispatchNameRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.scan = method('module/island/production.py', 'IslandProduction',
                           'scan_korean_dispatch_stocks', KoreanRecipeNameUnknown=UnknownName,
                           DIC_ISLAND_PRODUCTION_PLACE={1: {'slot': [1, 2, 3]}, 2: {'slot': [4]}},
                           DIC_ISLAND_SLOT={k: {'formula': [1] if k != 3 else [2],
                                                'activity_formula': []} for k in range(1, 5)},
                           page_island_manage=Mock(), del_cached_property=Mock())
        self.ui = Mock()
        self.ui.kr_verified_recipe_slots = {1, 2, 3, 4}

    def test_only_same_facility_formula_siblings_revoked_before_spending(self):
        self.ui.scan_all_recipe_stocks.side_effect = UnknownName()
        self.assertIsNone(self.scan(self.ui, 1, False))
        self.assertEqual(self.ui.kr_verified_recipe_slots, {3, 4})
        self.ui.ui_back.assert_called_once()
        self.ui.device.click.assert_not_called()

    def test_audit_and_unrecognized_page_keep_existing_failure(self):
        self.ui.scan_all_recipe_stocks.side_effect = UnknownName()
        for audit, recognized in [(True, True), (False, False)]:
            self.ui.is_in_recipe_menu.return_value = recognized
            with self.assertRaises(UnknownName):
                self.scan(self.ui, 1, audit)
        self.ui.ui_back.assert_not_called()

    def test_counter_or_other_error_is_not_suppressed(self):
        self.ui.scan_all_recipe_stocks.side_effect = RuntimeError('stock conflict')
        with self.assertRaises(RuntimeError):
            self.scan(self.ui, 1, False)
        self.ui.ui_back.assert_not_called()

    def test_good_stock_evidence_passes_unchanged(self):
        self.ui.scan_all_recipe_stocks.return_value = {101007: 18}
        self.assertEqual(self.scan(self.ui, 1, False), {101007: 18})
        self.ui.ui_back.assert_not_called()
