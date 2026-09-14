import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock


class PotatoTrialTest(unittest.TestCase):
    def test_trial_has_one_click_and_no_purchase_or_exchange_calls(self):
        import ast
        tree = ast.parse(Path('module/island/potato_trial.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'run_trial')
        calls = [n.func.attr for n in ast.walk(method) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)]
        self.assertEqual(calls.count('click'), 1)
        for forbidden in ('run_recipe', 'prepare_ingredients', 'island_shop_buy', 'island_shop_exchange', 'appear_then_click'):
            self.assertNotIn(forbidden, calls)

    def test_tool_captures_before_running(self):
        import ast
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'island_production_trial')
        calls = [n.value.func.attr for n in method.body if isinstance(n, ast.Expr)
                 and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)]
        self.assertIn('screenshot', calls)
        self.assertLess(calls.index('screenshot'), calls.index('run'))
        set_server_line = next(n.lineno for n in ast.walk(method) if isinstance(n, ast.Call)
                               and isinstance(n.func, ast.Name) and n.func.id == 'set_server')
        production_import = next(n.lineno for n in ast.walk(method) if isinstance(n, ast.ImportFrom)
                                 and n.module == 'module.island.production')
        self.assertLess(set_server_line, production_import)
        setter = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name) and n.func.id == 'set_server')
        self.assertEqual(setter.args[0].attr, 'Emulator_PackageName')

    def test_refuses_wrong_recipe_amount_and_insufficient_seed(self):
        from module.island.potato_trial import validate_trial
        for active, amount, counters in [(101008, 1, [(45,9,36)]),
                                         (101007, 2, [(45,18,27)]),
                                         (101007, 1, [(8,9,-1)]),
                                         (101007, 1, [(45,8,37)]),
                                         (101007, 1, [])]:
            with self.subTest(active=active, amount=amount, counters=counters):
                self.assertFalse(validate_trial(active, amount, counters))
        self.assertTrue(validate_trial(101007, 1, [(45,9,36)]))

    def test_receipt_cannot_be_reused(self):
        from module.island.potato_trial import reserve_attempt
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'attempt.json'
            reserve_attempt(path)
            with self.assertRaises(FileExistsError):
                reserve_attempt(path)
