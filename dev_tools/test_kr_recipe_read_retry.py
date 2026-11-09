"""Bounded read-only resampling: never accept moving/conflicting rows."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest
import module.config.server as server
import module.island_handler.recipe as recipe


class RecipeReadRetryTest(unittest.TestCase):
    def make(self):
        grid = Mock()
        grid.crop.return_value.buttons = [SimpleNamespace(area=(10,20,150,50)),
                                          SimpleNamespace(area=(10,170,150,200))]
        ui = SimpleNamespace(recipe_grid=grid, get_recipe_grid=Mock(return_value=grid),
                             image_crop=Mock(return_value='pixels'), working_slot_id=1,
                             device=Mock(), is_in_recipe_menu=Mock(return_value=True))
        return ui

    def run_reads(self, ui, reads):
        with patch.object(server,'server','kr'), patch.object(recipe,'RECIPE_PRODUCT_NAME_OCR') as ocr, \
                patch.object(recipe,'recipe_product_name_to_recipe_id', side_effect=lambda n,**kw: {'A':1,'B':2,'C':3}.get(n)):
            ocr.ocr.side_effect = reads
            return recipe.IslandRecipe.get_recipe_ids(ui)

    def test_unknown_recovers_only_after_two_matching_full_reads(self):
        ui = self.make()
        self.assertEqual(self.run_reads(ui,[['A','?'],['A','B'],['A','B']]),[1,2])
        self.assertEqual(ui.device.screenshot.call_count,2)
        ui.device.click.assert_not_called()
        ui.device.drag.assert_not_called()

    def test_persistent_unknown_has_a_finite_read_limit(self):
        ui = self.make()
        with self.assertRaises(recipe.KoreanRecipeNameUnknown):
            self.run_reads(ui,[['A','?']]*4)
        self.assertEqual(ui.device.screenshot.call_count,3)
        ui.device.click.assert_not_called()

    def test_conflicting_known_row_stops_without_replacing_identity(self):
        ui = self.make()
        with self.assertRaises(recipe.KoreanRecipeNameUnknown):
            self.run_reads(ui,[['A','?'],['C','B']])
        self.assertEqual(ui.device.screenshot.call_count,1)

    def test_grid_movement_is_not_treated_as_same_recipes(self):
        ui = self.make()
        moved = Mock()
        moved.crop.return_value.buttons=[SimpleNamespace(area=(10,25,150,55))]
        ui.get_recipe_grid.return_value=moved
        with self.assertRaises(recipe.KoreanRecipeNameUnknown):
            self.run_reads(ui,[['A','?']])
        self.assertEqual(ui.device.screenshot.call_count,1)

    def test_page_change_stops_without_reading_other_screen(self):
        ui=self.make()
        ui.is_in_recipe_menu.return_value=False
        with self.assertRaises(recipe.KoreanRecipeNameUnknown):
            self.run_reads(ui,[['A','?']])
        self.assertEqual(ui.device.screenshot.call_count,1)
