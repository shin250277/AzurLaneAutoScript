"""Scrolling must settle before the name and stock grids are cached together."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from module.island_handler.recipe import IslandRecipe
from module.exception import RequestHumanTakeover


def grid(y):
    return SimpleNamespace(buttons=[SimpleNamespace(area=(181,y,461,y+134))])


class RecipeSettleTest(unittest.TestCase):
    def make(self, rows):
        return SimpleNamespace(device=Mock(), is_in_recipe_menu=Mock(return_value=True),
                               get_recipe_grid=Mock(side_effect=rows))

    def test_moving_anchor_requires_three_identical_observations(self):
        rows = [grid(114),grid(108),grid(80),grid(80),grid(80)]
        ui = self.make(rows)
        IslandRecipe.settle_korean_recipe_grid(ui)
        self.assertIs(ui.recipe_grid,rows[-1])
        self.assertEqual(ui.device.screenshot.call_count,4)
        ui.device.click.assert_not_called()
        ui.device.drag.assert_not_called()

    def test_continuously_moving_rows_stop_with_bounded_reads(self):
        ui = self.make([grid(y) for y in range(100,160,10)])
        with self.assertRaises(RequestHumanTakeover):
            IslandRecipe.settle_korean_recipe_grid(ui)
        self.assertFalse(hasattr(ui,'recipe_grid'))

    def test_two_pixel_detection_jitter_keeps_latest_grid(self):
        rows = [grid(114),grid(112),grid(113)]
        ui = self.make(rows)
        IslandRecipe.settle_korean_recipe_grid(ui)
        self.assertIs(ui.recipe_grid,rows[-1])

    def test_count_changes_cannot_share_a_stability_window(self):
        empty = SimpleNamespace(buttons=[])
        ui = self.make([grid(114),empty]*3)
        with self.assertRaises(RequestHumanTakeover):
            IslandRecipe.settle_korean_recipe_grid(ui)
        self.assertLessEqual(ui.device.screenshot.call_count,6)
        ui.device.click.assert_not_called()

    def test_changed_page_never_publishes_a_grid(self):
        ui = self.make([grid(114)])
        ui.is_in_recipe_menu.return_value = False
        with self.assertRaises(RequestHumanTakeover):
            IslandRecipe.settle_korean_recipe_grid(ui)
        ui.get_recipe_grid.assert_not_called()
        self.assertFalse(hasattr(ui,'recipe_grid'))
