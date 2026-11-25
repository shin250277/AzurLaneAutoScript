"""Startup restart policy; no device or game inputs."""
import ast
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest


class RestartRequestTest(unittest.TestCase):
    def skipped(self, first, task, when):
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        branch = next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                      and any(isinstance(x, ast.Str) and
                              x.s == 'Skip task `Restart` at scheduler start'
                              for x in ast.walk(n)))
        obj = SimpleNamespace(is_first_task=first,
                              config=SimpleNamespace(Scheduler_NextRun=when))
        return eval(compile(ast.Expression(branch.test), 'alas.py', 'eval'),
                    {'self': obj, 'task': task, 'datetime': datetime})

    def test_explicit_immediate_restart_is_not_skipped(self):
        self.assertFalse(self.skipped(True, 'Restart', datetime(2020, 1, 1)))

    def test_routine_restart_keeps_startup_skip(self):
        self.assertTrue(self.skipped(True, 'Restart', datetime(2026, 9, 10)))

    def test_later_restart_and_other_tasks_are_not_skipped(self):
        self.assertFalse(self.skipped(False, 'Restart', datetime(2026, 9, 10)))
        self.assertFalse(self.skipped(True, 'Commission', datetime(2020, 1, 1)))


if __name__ == '__main__':
    unittest.main()
