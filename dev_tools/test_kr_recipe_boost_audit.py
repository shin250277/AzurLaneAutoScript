import unittest
import ast
import re
from pathlib import Path
from unittest.mock import Mock
from module.island.kr_preflight import validate_recipe_counters


class BoostAuditTest(unittest.TestCase):
    def test_ocr_retains_observed_parts_without_inventing_bonus(self):
        tree = ast.parse(Path('module/island_handler/recipe.py').read_text(encoding='utf-8'))
        klass = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                     and n.name == 'IslandReversedDigitCounter')
        method = next(n for n in klass.body if isinstance(n, ast.FunctionDef)
                      and n.name == 'after_process')
        klass.body = [method]
        class Base:
            def after_process(self, value):
                return value
        scope = {'Ocr': Base, 're': re, 'logger': Mock()}
        exec(compile(ast.Module(body=[klass]), '<counter>', 'exec'), scope)
        counter = scope['IslandReversedDigitCounter']()
        counter.observed_components = []
        self.assertEqual(counter.after_process('0/(2+10)'), (0, 12, -12))
        self.assertEqual(counter.after_process('15/2'), (15, 2, 13))
        self.assertEqual(counter.after_process('0/(2+?)'), (0, 0, 0))
        self.assertEqual(counter.observed_components, [(2, 10), (2, 0)])

    def test_observed_base_plus_boost_requires_explicit_parts(self):
        args = ({3000: 2}, 1, [(0, 12, -12)])
        self.assertFalse(validate_recipe_counters(*args, require_available=False))
        self.assertTrue(validate_recipe_counters(*args, require_available=False,
                                                components=[(2, 10)]))
        for parts in ([(3, 9)], [(2, 9)], [], [(2, -1)]):
            self.assertFalse(validate_recipe_counters(*args, require_available=False,
                                                     components=parts))
        # The diagnostic exception must never authorize spending.
        self.assertFalse(validate_recipe_counters({3000: 2}, 1, [(100, 12, 88)],
                                                 components=[(2, 10)]))
