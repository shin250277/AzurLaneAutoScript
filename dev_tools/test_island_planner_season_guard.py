"""Missing regional schedules are not an inactive season or a foreign schedule."""
import ast
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest


class PlannerSeasonGuardTest(unittest.TestCase):
    def test_kr_keeps_current_season_after_foreign_rollover(self):
        from module.island.data import DIC_ISLAND_SEASON
        tree = ast.parse(Path('module/island_handler/production_plan_calculator.py').read_text(encoding='utf-8'))
        tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name == 'get_current_activity_list']
        scope = dict(datetime=datetime, server=SimpleNamespace(server='kr'),
                     DIC_ISLAND_SEASON=DIC_ISLAND_SEASON)
        exec(compile(tree, 'calculator.py', 'exec'), scope)
        lookup = scope['get_current_activity_list']
        for day in (5, 9, 18):
            self.assertEqual(lookup(datetime(2026, 11, day, 23)),
                             [990022, 990023, 990024, 990025])
        # No invented new-season schedule or foreign fallback after known data.
        self.assertIsNone(lookup(datetime(2026, 11, 20)))

    def test_task_mapping_excludes_exact_season_end(self):
        tree = ast.parse(Path('module/island/season_task.py').read_text(encoding='utf-8'))
        condition = next(n for n in ast.walk(tree) if isinstance(n, ast.Compare)
                         and isinstance(n.left, ast.Name) and n.left.id == 'season_start')
        expression = ast.Expression(body=condition)
        at_end = dict(season_start=datetime(2026, 8, 20),
                      server_now=datetime(2026, 11, 19, 12),
                      season_end=datetime(2026, 11, 19, 12))
        self.assertFalse(eval(compile(expression, 'season_boundary', 'eval'), at_end))

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
