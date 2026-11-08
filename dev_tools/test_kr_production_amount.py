import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class ProductionAmountTest(unittest.TestCase):
    def make_ui(self, readings):
        tree = ast.parse(Path('module/island_handler/recipe.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'set_recipe_batch_count')]
        scope = dict(ISLAND_RECIPE_AMOUNT_OCR=SimpleNamespace(ocr=Mock(side_effect=readings)),
                     ISLAND_RECIPE_AMOUNT_PLUS='plus', ISLAND_RECIPE_AMOUNT_MINUS='minus')
        exec(compile(tree, 'recipe', 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                             is_in_recipe_menu=lambda: True,
                             loop=Mock(return_value=iter(readings)),
                             appear_then_click=Mock(return_value=True))
        return scope['set_recipe_batch_count'], ui

    def test_adjusts_one_observed_step_without_max_or_multiclick(self):
        run, ui = self.make_ui([1, 2, 3])
        self.assertTrue(run(ui, 3))
        self.assertEqual(ui.appear_then_click.call_count, 2)
        self.assertTrue(all(c[0][0] == 'plus' for c in ui.appear_then_click.call_args_list))
        ui.device.multi_click.assert_not_called()
        ui.loop.assert_called_once_with(skip_first=False, timeout=30)

    def test_invalid_request_or_ocr_cannot_click(self):
        for count in (True, 0, -1, float('inf'), 1.5):
            run, ui = self.make_ui([1])
            self.assertFalse(run(ui, count))
            ui.appear_then_click.assert_not_called()
        for value in (True, 0, -1, 1.5):
            run, ui = self.make_ui([value])
            self.assertFalse(run(ui, 3))
            ui.appear_then_click.assert_not_called()

    def test_decrease_and_timeout_never_claim_success(self):
        run, ui = self.make_ui([3, 2])
        self.assertTrue(run(ui, 2))
        ui.appear_then_click.assert_called_once_with('minus', offset=(20, 20), interval=0.3)
        run, ui = self.make_ui([1, 1])
        self.assertFalse(run(ui, 2))

    def test_leaving_recipe_cannot_click(self):
        run, ui = self.make_ui([1])
        ui.is_in_recipe_menu = lambda: False
        self.assertFalse(run(ui, 2))
        ui.appear_then_click.assert_not_called()
