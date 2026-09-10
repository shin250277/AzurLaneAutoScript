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
    def test_guild_mode_retains_inactive_or_unknown_kr_frame_only(self):
        method = load_method(
            'module/guild/operations.py', '_guild_operations_get_mode',
            GUILD_OPERATIONS_INACTIVE_CHECK='inactive',
            GUILD_BOSS_ENTER='boss', GUILD_OPERATIONS_NEW='new')
        for server in ('kr', 'jp'):
            for mode in ('inactive', 'active', 'boss', 'new', 'unknown'):
                with self.subTest(server=server, mode=mode):
                    ui = SimpleNamespace(
                        config=SimpleNamespace(SERVER=server), device=Mock(),
                        appear=Mock(side_effect=lambda button, **kw: button == mode),
                        _guild_operations_active_appear=Mock(
                            return_value=mode in ('inactive', 'active')))
                    expected = {'inactive': 0, 'active': 1, 'boss': 2, 'new': 2}.get(mode)
                    self.assertEqual(method(ui), expected)
                    if server == 'kr' and mode in ('inactive', 'unknown'):
                        ui.device.image_save.assert_called_once_with(
                            './log/kr_guild_operations_{}.png'.format(mode))
                    else:
                        ui.device.image_save.assert_not_called()
                    self.assertEqual(ui.device.screenshot.call_count, 2 if mode == 'unknown' else 0)
                    ui.device.click.assert_not_called()

    def test_research_center_unknown_retains_current_kr_frame_once(self):
        statuses = [Mock() for _ in range(5)]
        detail = Mock()
        method = load_method(
            'module/research/ui.py', 'get_research_status',
            RESEARCH_STATUS=statuses, RESEARCH_SCALING=[1] * 5,
            crop=Mock(), rgb2gray=Mock(),
            TEMPLATE_WAITING=Mock(match=Mock(return_value=False)),
            TEMPLATE_RUNNING=Mock(match=Mock(return_value=False)),
            TEMPLATE_DETAIL=detail)
        for server, current in (('kr', True), ('jp', True), ('kr', False)):
            with self.subTest(server=server, current=current):
                device = Mock()
                ui = SimpleNamespace(config=SimpleNamespace(SERVER=server), device=device)
                frame = device.image if current else object()
                for _ in range(2):
                    detail.match.side_effect = [True, True, False, True, True]
                    self.assertEqual(method(ui, frame),
                                     ['detail', 'detail', 'unknown', 'detail', 'detail'])
                if server == 'kr' and current:
                    device.image_save.assert_called_once_with('./log/kr_research_center_unknown.png')
                else:
                    device.image_save.assert_not_called()
                device.click.assert_not_called()

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
