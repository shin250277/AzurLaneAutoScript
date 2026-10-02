"""A delayed reward must be handled before declaring search unavailable."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock


class SearchUnlockTest(unittest.TestCase):
    def make_daemon(self):
        path = Path('module/os/map.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'os_auto_search_daemon')
        tree.body = [method]
        class Takeover(Exception):
            pass
        timer = Mock()
        timer.start.return_value = timer
        timer.reached.return_value = True
        scope = dict(Timer=Mock(return_value=timer), logger=Mock(),
                     RequestHumanTakeover=Takeover,
                     AUTO_SEARCH_OS_MAP_OPTION_OFF='off',
                     AUTO_SEARCH_OS_MAP_OPTION_OFF_DISABLED='disabled',
                     AUTO_SEARCH_OS_MAP_OPTION_ON='on')
        exec(compile(tree, str(path), 'exec'), scope)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.timer_factory = scope['Timer']
        ui.loop.return_value = iter([None])
        ui.is_in_map.return_value = False
        ui.appear.return_value = False
        ui.handle_os_auto_search_map_option.return_value = False
        return scope[method.name], ui, Takeover

    def test_reward_arriving_at_timeout_is_handled_first(self):
        daemon, ui, _ = self.make_daemon()
        class RewardComplete(Exception):
            pass
        ui.handle_os_auto_search_map_option.side_effect = RewardComplete
        with self.assertRaises(RewardComplete):
            daemon(ui)

    def test_option_arriving_at_timeout_is_accepted(self):
        daemon, ui, _ = self.make_daemon()
        ui.appear.return_value = True
        ui.handle_os_auto_search_map_option.return_value = True
        self.assertEqual(daemon(ui), 0)

    def test_unknown_screen_still_stops(self):
        daemon, ui, takeover = self.make_daemon()
        with self.assertRaises(takeover):
            daemon(ui)
        ui.device.click.assert_not_called()

    def test_kr_transition_wait_is_bounded_and_diagnostic(self):
        daemon, ui, takeover = self.make_daemon()
        with self.assertRaises(takeover):
            daemon(ui)
        ui.timer_factory.assert_any_call(15, count=10)
        ui.device.image_save.assert_called_once_with('./log/kr_os_search_unavailable.png')

    def test_other_servers_keep_original_deadline(self):
        daemon, ui, takeover = self.make_daemon()
        ui.config.SERVER = 'jp'
        with self.assertRaises(takeover):
            daemon(ui)
        ui.timer_factory.assert_any_call(5, count=10)
        ui.device.image_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
