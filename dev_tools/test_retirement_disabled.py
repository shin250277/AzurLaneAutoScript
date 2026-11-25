"""Disabled rarity selections must not mutate dock filters or select ships."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def method(name):
    tree = ast.parse(Path('module/retire/retirement.py').read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == name)]
    scope = dict(RequestHumanTakeover=RuntimeError, logger=Mock(),
                 IN_RETIREMENT_CHECK='retire')
    exec(compile(tree, 'module/retire/retirement.py', 'exec'), scope)
    return scope[name]


class RetirementDisabledTest(unittest.TestCase):
    def test_empty_rarity_stops_before_any_dock_input(self):
        for rarity in (set(), [], ()):
            with self.subTest(rarity=rarity):
                ui = SimpleNamespace(_retire_amount=3000, _retire_rarity=rarity)
                with self.assertRaisesRegex(RuntimeError, 'no ship rarities'):
                    method('retire_ships_old')(ui)

    def test_full_popup_or_retire_screen_stops_before_click(self):
        for popup in (False, True):
            with self.subTest(popup=popup):
                ui = SimpleNamespace(config=SimpleNamespace(Retirement_RetireMode='old_retire'),
                    _retire_rarity=set(), retirement_appear=lambda: popup,
                    appear=lambda *args, **kwargs: not popup)
                with self.assertRaisesRegex(RuntimeError, 'free dock space manually'):
                    method('handle_retirement')(ui)

    def test_normal_screen_keeps_existing_tips_handling(self):
        ui = SimpleNamespace(config=SimpleNamespace(Retirement_RetireMode='old_retire'),
            _retire_rarity=set(), retirement_appear=lambda: False,
            appear=lambda *args, **kwargs: False, handle_game_tips=lambda: True)
        self.assertTrue(method('handle_retirement')(ui))


if __name__ == '__main__':
    unittest.main()
