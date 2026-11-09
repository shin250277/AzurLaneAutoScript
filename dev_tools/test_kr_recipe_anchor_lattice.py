import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import module.config.server as server
from module.island_handler.recipe import IslandRecipe


class RecipeAnchorLatticeTest(unittest.TestCase):
    def grid(self, ys, region='kr'):
        ui = SimpleNamespace(_get_recipe_buttons=lambda: np.array([(0,y) for y in ys]))
        with patch.object(server, 'server', region):
            return IslandRecipe.get_recipe_grid(ui)

    def test_three_consistent_rows_exclude_observed_top_decoration(self):
        actual = self.grid([6,39,188,337])
        self.assertEqual([b.area[1] for b in actual.buttons], [94,243,392])

    def test_only_two_supporting_rows_do_not_infer_a_lattice(self):
        self.assertEqual([b.area for b in self.grid([39,100,188]).buttons],
                         [b.area for b in self.grid([39,100,188], 'en').buttons])

    def test_normal_four_rows_are_preserved(self):
        self.assertEqual([b.area[1] for b in self.grid([59,208,357,506]).buttons],
                         [114,263,412,561])

    def test_foreign_server_path_unchanged(self):
        self.assertEqual(self.grid([6,39,188,337], 'en').buttons[0].area[1],61)

    def test_missing_middle_row_does_not_authorize_lattice_filter(self):
        ys = [6, 39, 188, 486]
        # Keep the original KR header exclusion, not the inferred 94px row.
        self.assertEqual([b.area[1] for b in self.grid(ys).buttons], [210, 359, 508])

    def test_competing_lattices_are_not_arbitrarily_selected(self):
        ys = [39, 70, 188, 219, 337, 368]
        self.assertEqual([b.area for b in self.grid(ys).buttons],
                         [b.area for b in self.grid(ys, 'en').buttons])
