"""Preflight must preserve targets and reject incomplete spending evidence."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def method(path, name, **scope):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == name)]
    scope.update(RequestHumanTakeover=RuntimeError, logger=Mock())
    exec(compile(tree, path, 'exec'), scope)
    return scope[name]


class PreflightTest(unittest.TestCase):
    def test_incomplete_season_scan_preserves_targets(self):
        scan = method('module/island/season_task.py', 'scan_all',
                      ISLAND_SEASON_TASK_SCROLL=Mock())
        for names, buttons in [([], []), ([1], [1, 2])]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.task_names = names
            ui.season_task_grid.buttons = buttons
            with self.assertRaisesRegex(RuntimeError, 'Incomplete KR season scan'):
                scan(ui)
            ui.config.cross_set.assert_not_called()
            ui.device.click.assert_not_called()

    def test_audit_reads_all_targets_without_applying_or_claiming(self):
        log = Mock()
        audit = method('module/island/season_task.py', 'audit_korean_season',
                       page_island_season='season', del_cached_property=Mock(),
                       DIC_ISLAND_TASK={1: {'target': {10: 2, 20: 3}},
                                        2: {'target': {10: 4}}})
        audit.__globals__['logger'] = log
        ui = Mock()
        ui.scan_all.return_value = [1, 2]
        with self.assertRaisesRegex(RuntimeError, 'target update remains blocked'):
            audit(ui)
        log.attr.assert_any_call('KR season audit candidate (not applied)', {10: 6, 20: 3})
        ui.config.cross_set.assert_not_called()
        ui.receive_all_reward.assert_not_called()
        ui.device.click.assert_not_called()

    def test_season_audit_never_overwrites_targets_or_collects(self):
        run = method('module/island/season_task.py', 'run', page_island_season='season')
        ui = SimpleNamespace(config=Mock(SERVER='kr'), ui_ensure=Mock(),
                             island_season_bottom_navbar_ensure=Mock(),
                             audit_korean_season=Mock(), receive_all_reward=Mock())
        run(ui)
        ui.audit_korean_season.assert_called_once_with()
        ui.receive_all_reward.assert_not_called()
        ui.config.cross_set.assert_not_called()

    def test_counter_validator_requires_exact_cost_and_arithmetic(self):
        from module.island.kr_preflight import validate_recipe_counters
        self.assertTrue(validate_recipe_counters({1005: 9}, 1, [(20, 9, 11)]))
        self.assertFalse(validate_recipe_counters({1005: 9}, 1, [(0, 9, -9)]))
        self.assertTrue(validate_recipe_counters({1005: 9}, 1, [(0, 9, -9)], require_available=False))
        for amount, counters in [(0, [(20, 9, 11)]), (2, [(20, 9, 11)]),
                                 (1, []), (1, None), (1, [(20, 8, 12)]),
                                 (1, [(20, 9, 12)]), (1, [(8, 9, -1)]),
                                 (1, [(20, 9, 11), (20, 9, 11)]),
                                 (1, [(20, 9)]), (True, [(20, 9, 11)])]:
            with self.subTest(amount=amount, counters=counters):
                self.assertFalse(validate_recipe_counters({1005: 9}, amount, counters))

    def test_multiple_ingredients_and_batch_total(self):
        from module.island.kr_preflight import validate_recipe_counters
        self.assertTrue(validate_recipe_counters({1: 2, 2: 3}, 2,
                                                [(10, 4, 6), (9, 6, 3)]))
        self.assertFalse(validate_recipe_counters({1: 2, 2: 3}, 2, [(10, 4, 6)]))


if __name__ == '__main__':
    unittest.main()
