"""A battle result during KR zone identification must not block globe exit."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock


class GlobeResultTest(unittest.TestCase):
    def run_exit(self, server, results=True):
        path = Path('module/os/globe_operation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'os_map_goto_globe')]
        scope = dict(logger=Mock(), Timer=Mock(), MAP_GOTO_GLOBE='globe',
                     MAP_GOTO_GLOBE_FOG='fog', PORT_CHECK='port', BACK_ARROW='back',
                     AUTO_SEARCH_REWARD='reward', RewardUncollectedError=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        ui = Mock()
        ui.config.SERVER = server
        ui.loop.side_effect = [iter([0, 1, 2]), iter([0])]
        ui.is_in_globe.side_effect = [False, False, True]
        ui.is_zone_pinned.return_value = True
        ui.appear_then_click.return_value = False
        ui.appear.return_value = False
        ui.handle_battle_status.side_effect = [results, False]
        ui.handle_exp_info.return_value = results
        ui.handle_map_event.return_value = False
        ui.handle_popup_confirm.return_value = False
        scope['os_map_goto_globe'](ui, unpin=False)
        return ui

    def test_kr_handles_result_then_experience_before_map_clicks(self):
        ui = self.run_exit('kr')
        self.assertEqual(ui.handle_battle_status.call_count, 2)
        ui.handle_exp_info.assert_called_once_with()
        ui.appear_then_click.assert_not_called()
        ui.device.click.assert_not_called()

    def test_other_server_keeps_existing_navigation(self):
        ui = self.run_exit('jp')
        ui.handle_battle_status.assert_not_called()
        ui.handle_exp_info.assert_not_called()

    def test_unknown_overlay_does_not_get_a_blind_result_click(self):
        ui = self.run_exit('kr', results=False)
        self.assertEqual(ui.handle_battle_status.call_count, 2)
        self.assertEqual(ui.handle_exp_info.call_count, 2)
        ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
