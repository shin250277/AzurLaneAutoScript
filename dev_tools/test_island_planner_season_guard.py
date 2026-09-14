"""Missing regional schedules are not an inactive season or a foreign schedule."""
import ast
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest


class PlannerSeasonGuardTest(unittest.TestCase):
    def test_missing_regional_dates_have_actionable_error(self):
        tree = ast.parse(Path('module/island_handler/production_plan_calculator.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'get_current_activity_list')]
        scope = dict(datetime=datetime, server=SimpleNamespace(server='kr'),
                     DIC_ISLAND_SEASON={1: {'start_time': {'jp': '2026-01-01 00:00:00'},
                                           'end_time': {'jp': '2026-12-31 00:00:00'},
                                           'activity': [1]}})
        exec(compile(tree, 'calculator.py', 'exec'), scope)
        with self.assertRaisesRegex(ValueError, 'Missing.*kr.*season'):
            scope['get_current_activity_list'](datetime(2026, 9, 14))
