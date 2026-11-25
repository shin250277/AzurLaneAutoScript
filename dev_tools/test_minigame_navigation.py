"""A fading game-room button must not be treated as the game list."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def load_method(name, scroll):
    path = 'module/minigame/minigame.py'
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == name)]
    scope = dict(logger=Mock(), MINIGAME_SCROLL=scroll,
                 GAME_ROOM_CHECK='header', GOTO_CHOOSE_GAME='choose',
                 BACK='back', COIN_POPUP='popup', COIN='coin',
                 page_academy='academy', ACADEMY_GOTO_GAME_ROOM='enter')
    exec(compile(tree, path, 'exec'), scope)
    return scope[name]


class MinigameNavigationTest(unittest.TestCase):
    def test_back_requires_positive_game_list_evidence(self):
        for name in ('go_to_main_page', 'collect_coin'):
            for is_list in (False, True):
                with self.subTest(method=name, is_list=is_list):
                    frame = [0]
                    def next_frame():
                        frame[0] += 1
                        self.assertLess(frame[0], 3, 'navigation did not finish')
                    scroll = Mock()
                    scroll.appear.return_value = is_list
                    ui = SimpleNamespace(
                        device=Mock(screenshot=Mock(side_effect=next_frame)),
                        ui_additional=Mock(return_value=False),
                        appear=Mock(side_effect=lambda button, **kw:
                                    button == 'header' or
                                    (button == 'choose' and frame[0] > 0)),
                        appear_then_click=Mock(return_value=False))
                    load_method(name, scroll)(ui)
                    backs = [c for c in ui.appear_then_click.call_args_list
                             if c[0][0] == 'back']
                    self.assertEqual(len(backs), int(is_list))

    def test_game_entry_recovers_observed_academy(self):
        frame = [0]
        def next_frame():
            frame[0] += 1
            self.assertLess(frame[0], 3, 'entry did not finish')
        scroll = Mock()
        scroll.appear.return_value = True
        ui = SimpleNamespace(
            device=Mock(screenshot=Mock(side_effect=next_frame)),
            ui_page_appear=Mock(side_effect=lambda page, **kw: frame[0] == 0),
            appear=Mock(side_effect=lambda button, **kw:
                        button == 'header' and frame[0] > 0),
            appear_then_click=Mock(return_value=False),
            deal_popup=Mock(return_value=False), choose_game=Mock(),
            use_coin=Mock(return_value=False), play_game=Mock(), exit_game=Mock())
        self.assertFalse(load_method('minigame_run', scroll)(ui))
        ui.device.click.assert_called_once_with('enter')
        ui.play_game.assert_not_called()


if __name__ == '__main__':
    unittest.main()
