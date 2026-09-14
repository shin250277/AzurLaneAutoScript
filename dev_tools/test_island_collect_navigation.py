"""Unknown collection screens must not be daily success or unbounded waits."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


def method(name):
    tree = ast.parse(Path('module/island/collect.py').read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == name)]
    scope = dict(logger=Mock(), page_island_manage='manage',
        ISLAND_COLLECT_SELECT_ENTER='enter', ISLAND_COLLECT_SELECT_CONFIRM='confirm',
        ISLAND_COLLECT_SELECT_CANCEL='cancel')
    exec(compile(tree, 'module/island/collect.py', 'exec'), scope)
    return scope[name]


class IslandCollectNavigationTest(unittest.TestCase):
    def test_collection_controls_have_korean_assets(self):
        tree = ast.parse(Path('module/island/assets.py').read_text(encoding='utf-8'))
        for suffix in ('ENTER', 'CONFIRM', 'CANCEL'):
            name = 'ISLAND_COLLECT_SELECT_' + suffix
            call = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                        and n.targets[0].id == name)
            files = ast.literal_eval(next(k.value for k in call.keywords if k.arg == 'file'))
            self.assertEqual(files['kr'], './assets/kr/island/{}.png'.format(name))
            self.assertTrue(Path(files['kr']).is_file())

    def test_missing_enter_is_unknown_and_saves_diagnostic(self):
        ui = SimpleNamespace(loop=lambda **kw: iter([]), config=SimpleNamespace(SERVER='kr'), device=Mock())
        self.assertIsNone(method('collect_available')(ui))
        ui.device.image_save.assert_called_once()

    def test_unknown_screen_defers_without_waiting_or_collecting(self):
        ui = SimpleNamespace(ui_ensure=Mock(), island_manage_side_navbar_ensure=Mock(),
            collect_available=lambda: None, config=Mock())
        self.assertFalse(method('run')(ui))
        ui.config.task_delay.assert_called_once_with(success=False)

    def test_failed_return_is_bounded_and_not_daily_success(self):
        ui = SimpleNamespace(ui_ensure=Mock(), island_manage_side_navbar_ensure=Mock(),
            collect_available=lambda: False, config=Mock(), loop=Mock(return_value=iter([])))
        self.assertFalse(method('run')(ui))
        ui.loop.assert_called_once_with(timeout=10)
        ui.config.task_delay.assert_called_once_with(success=False)


if __name__ == '__main__':
    unittest.main()
