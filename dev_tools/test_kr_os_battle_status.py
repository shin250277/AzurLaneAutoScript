"""KR OpSi may leave a successful result screen awaiting a tap."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class KRResultTest(unittest.TestCase):
    def run_handler(self, server, generic_result):
        path = Path('module/os_combat/combat.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'handle_auto_search_battle_status')]
        scope = dict(BATTLE_STATUS_C='C', BATTLE_STATUS_D='D', logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                             battle_status_click_interval=1, appear=Mock(return_value=False),
                             handle_battle_status=Mock(return_value=generic_result))
        return scope['handle_auto_search_battle_status'](ui), ui

    def test_kr_uses_existing_result_handler(self):
        result, ui = self.run_handler('kr', True)
        self.assertTrue(result)
        ui.handle_battle_status.assert_called_once_with(drop=None)

    def test_unknown_screen_is_not_success(self):
        result, ui = self.run_handler('kr', False)
        self.assertFalse(result)

    def test_other_servers_keep_original_path(self):
        result, ui = self.run_handler('jp', True)
        self.assertFalse(result)
        ui.handle_battle_status.assert_not_called()


if __name__ == '__main__':
    unittest.main()
