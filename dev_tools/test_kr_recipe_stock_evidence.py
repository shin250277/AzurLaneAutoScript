"""Incomplete OCR must not become a partial production inventory."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped
from module.island.kr_preflight import verified_recipe_stocks


class RecipeStockEvidenceTest(unittest.TestCase):
    def test_zero_stock_and_matching_overlap_are_valid(self):
        previous = {101: 0}
        self.assertEqual(verified_recipe_stocks([101, 102], [0, 52], previous),
                         {101: 0, 102: 52})
        self.assertEqual(previous, {101: 0})

    def test_truncated_extra_or_missing_ocr_is_rejected(self):
        for ids, stocks in (([101, 102], [5]), ([101], [5, 6]), ([], []), ([101], None)):
            self.assertIsNone(verified_recipe_stocks(ids, stocks, {}))

    def test_duplicate_invalid_or_conflicting_values_are_rejected(self):
        for ids, stocks in (([101, 101], [5, 5]), ([None], [0]), ([True], [0]),
                            ([0], [0]), ([101], [-1]), ([101], [True]),
                            ([101], ['5']), ([101], [5.5])):
            self.assertIsNone(verified_recipe_stocks(ids, stocks, {}))
        self.assertIsNone(verified_recipe_stocks([101], [20], {101: 0}))

    def test_live_scan_stops_before_scrolling_incomplete_page(self):
        scan = method('module/island_handler/recipe.py', 'IslandRecipe',
                      'scan_all_recipe_stocks', server=SimpleNamespace(server='kr'),
                      ISLAND_RECIPE_AMOUNT_MAX=object(), ISLAND_RECIPE_DRAG_CHECK=Mock())
        ui = Mock()
        ui.loop.return_value = [None]
        ui.appear.return_value = True
        ui.recipe_ids = [101, 102]
        ui.get_recipe_product_stocks.return_value = [5]
        with self.assertRaises(TaskStopped):
            scan(ui)
        ui.next_recipe_page.assert_not_called()
        ui.device.image_save.assert_called_once_with('./log/kr_island_stock_unknown.png')

    def test_timeout_is_not_reported_as_complete_inventory(self):
        scan = method('module/island_handler/recipe.py', 'IslandRecipe',
                      'scan_all_recipe_stocks', server=SimpleNamespace(server='kr'),
                      ISLAND_RECIPE_AMOUNT_MAX=object(), ISLAND_RECIPE_DRAG_CHECK=Mock())
        ui = Mock()
        ui.loop.return_value = [None]
        ui.appear.return_value = True
        ui.recipe_ids = [101]
        ui.get_recipe_product_stocks.return_value = [0]
        with self.assertRaises(TaskStopped):
            scan(ui)
        # One matching frame is insufficient; no false completion on timeout.
        ui.next_recipe_page.assert_called_once_with()

    def test_confirmed_bottom_returns_complete_inventory(self):
        scan = method('module/island_handler/recipe.py', 'IslandRecipe',
                      'scan_all_recipe_stocks', server=SimpleNamespace(server='kr'),
                      ISLAND_RECIPE_AMOUNT_MAX=object(), ISLAND_RECIPE_DRAG_CHECK=Mock())
        ui = Mock()
        ui.loop.return_value = [None, None]
        ui.appear.return_value = True
        ui.recipe_ids = [101]
        ui.get_recipe_product_stocks.return_value = [0]
        self.assertEqual(scan(ui), {101: 0})
        ui.device.image_save.assert_not_called()
