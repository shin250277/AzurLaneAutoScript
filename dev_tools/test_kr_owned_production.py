import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from datetime import timedelta
from module.island.kr_preflight import owned_batch_limit, owned_start_verified


class OwnedProductionTest(unittest.TestCase):
    def test_start_click_is_single_and_uncertain_outcome_stops(self):
        from module.exception import RequestHumanTakeover
        tree = ast.parse(Path('module/island_handler/recipe.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'run_recipe')]
        amount = Mock(return_value=2)
        scope = dict(ISLAND_RECIPE_AMOUNT_OCR=SimpleNamespace(ocr=amount),
                     DIC_ISLAND_RECIPE={42: dict(commission_cost={1: 3})}, logger=Mock(),
                     ISLAND_RECIPE_TIME_ANCHOR='start',
                     page_island_manage=SimpleNamespace(check_button='manage'))
        exec(compile(tree, 'recipe', 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                             is_in_recipe_menu=lambda: True, set_recipe=lambda recipe: True,
                             prepare_ingredients=lambda *a, **kw: (True, 2),
                             set_recipe_batch_count=lambda count: True,
                             get_recipe_remain_time=lambda: timedelta(minutes=1),
                             get_active_recipe_id=lambda: 42,
                             get_recipe_ingredient_counters=lambda: [(30, 6, 24)],
                             kr_owned_protected={1: 24}, loop=lambda **kw: range(2),
                             match_template_color=Mock(return_value=True))
        self.assertEqual(scope['run_recipe'](ui, 42, 2), (timedelta(minutes=1), 2))
        ui.device.click.assert_called_once_with('start')
        ui.device.reset_mock()
        ui.match_template_color.return_value = False
        with self.assertRaisesRegex(RequestHumanTakeover, 'uncertain'):
            scope['run_recipe'](ui, 42, 2)
        ui.device.click.assert_called_once_with('start')
        ui.device.reset_mock()
        amount.return_value = 3
        with self.assertRaisesRegex(RequestHumanTakeover, 'evidence changed'):
            scope['run_recipe'](ui, 42, 2)
        ui.device.click.assert_not_called()
        ui.prepare_ingredients = Mock(return_value=(True, 2))
        ui.set_recipe_batch_count = Mock(return_value=False)
        self.assertIsNone(scope['run_recipe'](ui, 42, 2))
        ui.prepare_ingredients.assert_not_called()
        ui.device.click.assert_not_called()

    def test_final_amount_and_remaining_balance_rechecked(self):
        self.assertTrue(owned_start_verified({1: 3}, [(30, 6, 24)], 2, {1: 24}))
        self.assertFalse(owned_start_verified({1: 3}, [(30, 6, 24)], 2, {1: 25}))
        self.assertFalse(owned_start_verified({1: 3}, [(30, 3, 27)], 2, {}))
        self.assertFalse(owned_start_verified({1: 3}, [(30, 6, 25)], 2, {}))
        self.assertFalse(owned_start_verified({}, [], True, {}))
        self.assertTrue(owned_start_verified({}, [], 2, {}))

    def test_kr_prepare_never_reaches_purchase_or_exchange_path(self):
        tree = ast.parse(Path('module/island_handler/recipe.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'prepare_ingredients')]
        scope = dict(ISLAND_RECIPE_AMOUNT_OCR=SimpleNamespace(ocr=lambda image: 1),
                     DIC_ISLAND_RECIPE={42: dict(commission_cost={1: 3}, production_limit=20)})
        exec(compile(tree, 'recipe', 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=SimpleNamespace(image=None),
                             get_active_recipe_id=lambda: 42,
                             production_floor_items=({1: 5}, {1: 3}, {1: 4}),
                             get_task_target_items=lambda: {1: {'total_need_count': 3}},
                             get_recipe_ingredient_counters=lambda: [(30, 3, 27)])
        # No purchase/exchange/navigation methods exist on this test UI.
        self.assertEqual(scope['prepare_ingredients'](ui, 42, 9), (False, 5))
        self.assertEqual(scope['prepare_ingredients'](ui, 42, 2), (True, 2))
        ui.get_active_recipe_id = lambda: 99
        self.assertEqual(scope['prepare_ingredients'](ui, 42, 2), (False, 0))

    def test_preserves_all_reserves_and_caps_requested_batches(self):
        self.assertEqual(owned_batch_limit({1: 3, 2: 2}, [(30, 3, 27), (20, 2, 18)],
                                          9, 20, {1: 12, 2: 4}), 6)
        self.assertEqual(owned_batch_limit({1: 3}, [(30, 3, 27)], 2, 20, {}), 2)

    def test_insufficient_or_invalid_evidence_never_buys(self):
        for counters in (None, [], [(30, 3, 28)], [(30, 4, 26)], [(True, 3, -2)]):
            self.assertEqual(owned_batch_limit({1: 3}, counters, 4, 20, {}), 0)
        self.assertEqual(owned_batch_limit({1: 3}, [(30, 3, 27)], 4, 20, {1: 29}), 0)
        self.assertEqual(owned_batch_limit({1: 3}, [(30, 3, 27)], 4, 20, {1: -1}), 0)

    def test_invalid_requests_and_recipe_limits_rejected(self):
        for count in (True, 0, -1, 1.5, float('inf')):
            self.assertEqual(owned_batch_limit({1: 3}, [(30, 3, 27)], count, 20, {}), 0)
        self.assertEqual(owned_batch_limit({1: 3}, [(30, 3, 27)], 9, 2, {}), 2)

    def test_free_recipe_requires_empty_complete_counters(self):
        self.assertEqual(owned_batch_limit({}, [], 3, 2, {}), 2)
        self.assertEqual(owned_batch_limit({}, None, 3, 2, {}), 0)
