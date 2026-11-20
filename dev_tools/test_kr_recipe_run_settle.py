import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island_handler.recipe import IslandRecipe


class RunSettleTest(unittest.TestCase):
    def test_fresh_grid_before_kr_dispatch_only(self):
        for region in ('kr', 'cn', 'jp', 'en'):
            ui = SimpleNamespace(recipe_id_sequence=[], recipe_grid='old',
                                 recipe_ids=['old'], settle_korean_recipe_grid=Mock())
            def settle():
                self.assertNotIn('recipe_grid', ui.__dict__)
                self.assertNotIn('recipe_ids', ui.__dict__)
                self.assertEqual(ui.working_slot_id, 9031)
            ui.settle_korean_recipe_grid.side_effect = settle
            with patch('module.island_handler.recipe.server.server', region):
                self.assertIsNone(IslandRecipe.run(ui, slot_id=9031))
            self.assertEqual(ui.settle_korean_recipe_grid.call_count, int(region == 'kr'))

    def test_unsettled_screen_never_starts_or_purchases(self):
        ui = SimpleNamespace(recipe_id_sequence=[(101013, None, None)],
                             settle_korean_recipe_grid=Mock(side_effect=RequestHumanTakeover('unstable')),
                             run_recipe=Mock())
        with patch('module.island_handler.recipe.server.server', 'kr'):
            with self.assertRaises(RequestHumanTakeover):
                IslandRecipe.run(ui, slot_id=9031)
        ui.run_recipe.assert_not_called()


if __name__ == '__main__':
    unittest.main()
