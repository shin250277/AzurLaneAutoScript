import ast
import unittest
from pathlib import Path


class RaidInspectTest(unittest.TestCase):
    def test_navigation_only_and_package_initialized_before_import(self):
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'raid_inspect')
        calls = [n.func.attr for n in ast.walk(method) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
        for forbidden in ('run', 'combat', 'raid_execute_once', 'raid_enter'):
            self.assertNotIn(forbidden, calls)
        self.assertIn('screenshot', calls)
        self.assertIn('ui_ensure', calls)
        initialize = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Name) and n.func.id == 'set_server')
        raid_import = next(n for n in ast.walk(method) if isinstance(n, ast.ImportFrom)
                           and n.module == 'module.raid.run')
        self.assertLess(initialize.lineno, raid_import.lineno)

    def test_trial_limits_and_retirement_disabled(self):
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'raid_trial')
        override = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute) and n.func.attr == 'override')
        values = {k.arg: ast.literal_eval(k.value) for k in override.keywords}
        self.assertEqual(values['StopCondition_RunCount'], 1)
        self.assertEqual(values['StopCondition_OilLimit'], 20000)
        self.assertEqual(values['Retirement_RetireMode'], 'old_retire')
        run = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and n.func.attr == 'run')
        self.assertEqual({k.arg: ast.literal_eval(k.value) for k in run.keywords}, {'total': 1})
        for key in ('Raid_UseTicket', 'TaskBalancer_Enable', 'OldRetire_N', 'OldRetire_R', 'OldRetire_SR', 'OldRetire_SSR'):
            self.assertIs(values[key], False)
