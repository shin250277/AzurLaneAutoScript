"""Header-occluded recipe rows must not become guessed product identities."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import numpy as np
import module.config.server as server
from module.island_handler.recipe import IslandRecipe, RECIPE_DETECT_AREA, RECIPE_DELTA


class VisibleRecipeRowsTest(unittest.TestCase):
    def test_name_context_changes_only_kr_crop_not_grid(self):
        import module.island_handler.recipe as recipe
        for region, expected in [('kr', (123, 19, 269, 50)), ('jp', (123, 23, 269, 46))]:
            grid = Mock()
            grid.crop.return_value.buttons = [SimpleNamespace(area=(304, 137, 450, 160))]
            ui = SimpleNamespace(recipe_grid=grid, image_crop=Mock(return_value='pixels'),
                                 working_slot_id=9401)
            with patch.object(server, 'server', region), patch.object(recipe, 'RECIPE_PRODUCT_NAME_OCR') as ocr, \
                    patch.object(recipe, 'recipe_product_name_to_recipe_id', return_value=2704):
                ocr.ocr.return_value = ['황광석']
                self.assertEqual(IslandRecipe.get_recipe_ids(ui), [2704])
            grid.crop.assert_called_once_with(expected, name='RECIPE_PRODUCT_NAME_GRID')
            ui.image_crop.assert_called_once_with((304, 137, 450, 160), copy=True)

    def test_single_ranch_off_grid_background_hit(self):
        def grid(ys, slot=9031, region='kr'):
            ui = SimpleNamespace(working_slot_id=slot,
                                 _get_recipe_buttons=lambda: np.array([(0, y) for y in ys]))
            with patch.object(server, 'server', region):
                return IslandRecipe.get_recipe_grid(ui)
        self.assertEqual(len(grid([59, 464]).buttons), 1)
        self.assertEqual(len(grid([59, 208]).buttons), 2)
        self.assertEqual(len(grid([90, 464]).buttons), 2)
        self.assertEqual(len(grid([59, 464], slot=None).buttons), 2)
        self.assertEqual(len(grid([59, 464], region='jp').buttons), 2)

    def grid(self, origin, count, region='kr'):
        rows = np.array([(0, origin - RECIPE_DETECT_AREA[1] + i * RECIPE_DELTA[1])
                         for i in range(count)])
        ui = SimpleNamespace(_get_recipe_buttons=lambda: rows)
        with patch.object(server, 'server', region):
            return IslandRecipe.get_recipe_grid(ui)

    def test_occluded_row_removed_with_same_name_stock_click_indices(self):
        grid = self.grid(61, 4)
        self.assertEqual(len(grid.buttons), 3)
        self.assertEqual(grid.origin[1], 61 + RECIPE_DELTA[1])
        self.assertTrue(grid.kr_scrollable)
        self.assertEqual(grid.crop((0, 23, 10, 46)).buttons[0].area[1],
                         grid.buttons[0].area[1] + 23)

    def test_two_visible_rows_still_scroll_when_raw_page_had_three(self):
        grid = self.grid(61, 3)
        self.assertEqual(len(grid.buttons), 2)
        self.assertTrue(grid.kr_scrollable)

    def test_full_top_page_and_foreign_layout_unchanged(self):
        for origin, count, region in [(114, 4, 'kr'), (61, 4, 'jp'), (114, 2, 'kr')]:
            grid = self.grid(origin, count, region)
            self.assertEqual(len(grid.buttons), count)
            self.assertEqual(grid.origin[1], origin)

    def test_known_single_recipe_ranch_not_removed(self):
        grid = self.grid(114, 1)
        self.assertEqual(len(grid.buttons), 1)
        self.assertEqual(grid.origin[1], 114)
        self.assertFalse(grid.kr_scrollable)

    def test_scroll_does_not_mistake_filtered_two_rows_for_list_end(self):
        for action in [IslandRecipe.next_recipe_page, IslandRecipe.prev_recipe_page]:
            ui = SimpleNamespace(recipe_grid=self.grid(61, 3), device=Mock())
            action(ui)
            ui.device.drag.assert_called_once()
            ui.device.screenshot.assert_called_once()

    def test_non_scrolling_single_recipe_does_not_drag(self):
        for action in [IslandRecipe.next_recipe_page, IslandRecipe.prev_recipe_page]:
            ui = SimpleNamespace(recipe_grid=self.grid(114, 1), device=Mock())
            action(ui)
            ui.device.drag.assert_not_called()
