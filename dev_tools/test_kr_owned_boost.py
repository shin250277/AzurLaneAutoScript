"""Explicit displayed ranch surcharges must preserve every stock reserve."""
import unittest
from collections import namedtuple
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from module.island import kr_preflight as checks
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class OwnedBoostTest(unittest.TestCase):
    def test_verified_one_batch_cost_includes_displayed_surcharge(self):
        cost = checks.verified_owned_unit_cost({3000: 2}, [(18, 12, 6)], [(2, 10)])
        self.assertEqual(cost, {3000: 12})
        self.assertEqual(checks.owned_batch_limit(cost, [(18, 12, 6)], 6, 20, {3000: 6}), 1)
        self.assertEqual(checks.owned_batch_limit(cost, [(18, 12, 6)], 6, 20, {3000: 7}), 0)

    def test_unknown_wrong_base_or_sum_never_becomes_a_cost(self):
        for parts in (None, [], [(3, 9)], [(2, 9)], [(2, -1)], [(True, 11)]):
            self.assertIsNone(checks.verified_owned_unit_cost({3000: 2}, [(18, 12, 6)], parts))
        self.assertIsNone(checks.verified_owned_unit_cost({3000: 2}, [(18, 12, 7)], [(2, 10)]))

    def test_final_linear_total_and_reserve_are_still_required(self):
        cost = checks.verified_owned_unit_cost({3000: 2}, [(100, 12, 88)], [(2, 10)])
        self.assertTrue(checks.owned_start_verified(cost, [(100, 24, 76)], 2, {3000: 76}))
        self.assertFalse(checks.owned_start_verified(cost, [(100, 24, 76)], 2, {3000: 77}))
        self.assertFalse(checks.owned_start_verified(cost, [(100, 25, 75)], 2, {}))

    def test_regular_and_empty_recipes_remain_strict(self):
        self.assertEqual(checks.verified_owned_unit_cost({1: 3}, [(30, 3, 27)], None), {1: 3})
        self.assertEqual(checks.verified_owned_unit_cost({}, [], None), {})
        self.assertIsNone(checks.verified_owned_unit_cost({}, None, None))

    def test_runtime_preparation_caps_ranch_and_rejects_non_ranch_surcharge(self):
        recipes = {key: dict(commission_cost={3000: 2}, production_limit=8)
                   for key in (101013, 42)}
        prepare = method('module/island_handler/recipe.py', 'IslandRecipe', 'prepare_ingredients',
                         ISLAND_RECIPE_AMOUNT_OCR=SimpleNamespace(ocr=lambda image: 1),
                         DIC_ISLAND_RECIPE=recipes)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=SimpleNamespace(image=None),
                             get_active_recipe_id=lambda: 101013,
                             production_floor_items=({3000: 2}, {3000: 2}, {3000: 1}),
                             get_task_target_items=lambda: {3000: {'total_need_count': 1}},
                             get_recipe_ingredient_counters=lambda: [(18, 12, 6)],
                             recipe_ingredient_components=[(2, 10)])
        self.assertEqual(prepare(ui, 101013, 6), (False, 1))
        self.assertEqual(ui.kr_owned_cost, (101013, {3000: 12}))
        self.assertEqual(ui.kr_owned_protected, {3000: 6})
        ui.get_active_recipe_id = lambda: 42
        self.assertEqual(prepare(ui, 42, 6), (False, 0))
        self.assertIsNone(ui.kr_owned_cost)  # no stale authorization

    def test_inventory_deducts_confirmed_total_not_only_declared_base(self):
        info = namedtuple('Info', 'stock batch_size')
        update = method('module/island_handler/recipe.py', 'IslandRecipe',
                        'update_recipe_id_sequence_and_stock',
                        DIC_ISLAND_RECIPE={101013: dict(commission_cost={3000: 2})},
                        get_recipe_product_id=lambda key: {101013: 2601, 9: 3000}[key])
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             kr_last_consumption=(101013, 2, {3000: 24}),
                             recipe_info_by_id={101013: info(0, 5), 9: info(100, 1)},
                             all_recipe_stocks={}, _build_recipe_id_sequence_to_run=Mock(return_value=[]))
        update(ui, 101013, 2)
        self.assertEqual(ui.all_recipe_stocks, {101013: 10, 9: 76})
        self.assertIsNone(ui.kr_last_consumption)
        with self.assertRaises(TaskStopped):
            update(ui, 101013, 2)

    def test_start_requires_same_base_parts_and_captures_total_consumption(self):
        from module.exception import RequestHumanTakeover
        run = method('module/island_handler/recipe.py', 'IslandRecipe', 'run_recipe',
                     ISLAND_RECIPE_AMOUNT_OCR=SimpleNamespace(ocr=lambda image: 2),
                     DIC_ISLAND_RECIPE={101013: dict(commission_cost={3000: 2})},
                     ISLAND_RECIPE_TIME_ANCHOR='start',
                     page_island_manage=SimpleNamespace(check_button='manage'))
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                             is_in_recipe_menu=lambda: True, set_recipe=lambda recipe: True,
                             set_recipe_batch_count=lambda count: True,
                             prepare_ingredients=lambda *args, **kwargs: (True, 2),
                             get_recipe_remain_time=lambda: timedelta(minutes=1),
                             get_active_recipe_id=lambda: 101013,
                             get_recipe_ingredient_counters=lambda: [(100, 24, 76)],
                             recipe_ingredient_components=[(4, 20)], kr_owned_protected={3000: 76},
                             kr_owned_cost=(101013, {3000: 12}), loop=lambda **kw: [None],
                             match_template_color=lambda *args, **kwargs: True)
        self.assertEqual(run(ui, 101013, 2), (timedelta(minutes=1), 2))
        self.assertEqual(ui.kr_last_consumption, (101013, 2, {3000: 24}))
        for parts in ([(5, 19)], [(4, 19)], None):
            ui.device.reset_mock()
            ui.recipe_ingredient_components = parts
            with self.assertRaises(RequestHumanTakeover):
                run(ui, 101013, 2)
            ui.device.click.assert_not_called()
