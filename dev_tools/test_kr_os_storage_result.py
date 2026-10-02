"""KR zone-entry battle results must not block storage navigation."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock


class StorageResultTest(unittest.TestCase):
    def run_entry(self, server):
        path = Path('module/os_handler/storage.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'storage_enter')]
        scope = dict(logger=Mock(), STORAGE_ENTER='enter', STORAGE_ENTER_PORT='port',
                     AUTO_SEARCH_REWARD='reward')
        exec(compile(tree, str(path), 'exec'), scope)
        ui = Mock()
        ui.config.SERVER = server
        ui.loop.return_value = iter([0, 1, 2])
        ui.is_in_storage.side_effect = [False, False, True]
        ui.appear_then_click.return_value = False
        ui.handle_battle_status.side_effect = [True, False]
        ui.handle_exp_info.return_value = True
        ui.handle_map_event.return_value = False
        scope['storage_enter'](ui)
        return ui

    def test_kr_dismisses_victory_then_experience(self):
        ui = self.run_entry('kr')
        self.assertEqual(ui.handle_battle_status.call_count, 2)
        ui.handle_exp_info.assert_called_once_with()
        ui.handle_map_event.assert_not_called()

    def test_other_servers_keep_existing_behavior(self):
        ui = self.run_entry('jp')
        ui.handle_battle_status.assert_not_called()
        ui.handle_exp_info.assert_not_called()


if __name__ == '__main__':
    unittest.main()
