"""Retain the actual timeout frame without adding game input."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def load_method(path, name, **scope):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == name)]
    scope.update(logger=Mock(), Timer=Mock())
    scope['Timer'].return_value.start.return_value.reached.return_value = True
    exec(compile(tree, path, 'exec'), scope)
    return scope[name]


class TimeoutDiagnosticsTest(unittest.TestCase):
    def test_research_timeout_retains_kr_frame_only(self):
        method = load_method('module/research/research.py', 'receive_6th_research')
        for server in ('kr', 'jp'):
            with self.subTest(server=server):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER=server), device=Mock(),
                                     research_has_finished=Mock(return_value=False),
                                     get_research_status=Mock(return_value=['unknown']))
                self.assertTrue(method(ui))
                if server == 'kr':
                    ui.device.image_save.assert_called_once_with('./log/kr_research_wait_timeout.png')
                else:
                    ui.device.image_save.assert_not_called()
                ui.device.click.assert_not_called()

    def test_dorm_timeout_retains_kr_frame_only(self):
        method = load_method('module/dorm/dorm.py', 'dorm_collect', DORM_QUICK_COLLECT='collect')
        for server in ('kr', 'jp'):
            with self.subTest(server=server):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER=server), device=Mock(),
                                     ensure_no_info_bar=Mock(), loop=lambda: iter([None]),
                                     ui_additional=Mock(return_value=False),
                                     appear_then_click=Mock(return_value=False),
                                     info_bar_count=Mock(return_value=0))
                method(ui)
                if server == 'kr':
                    ui.device.image_save.assert_called_once_with('./log/kr_dorm_collect_timeout.png')
                else:
                    ui.device.image_save.assert_not_called()
                ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
