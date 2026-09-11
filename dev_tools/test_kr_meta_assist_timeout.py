import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class KrMetaAssistTimeoutTest(unittest.TestCase):
    def test_empty_list_after_combat_retries_instead_of_daily_completion(self):
        path = Path('module/os_ash/meta.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AshBeaconAssist')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_attack_meta')
        tree.body = [method]
        timer = Mock()
        timer.start.return_value = timer
        timer.reached.side_effect = [False, True]
        scope = {'Timer': Mock(return_value=timer), 'logger': Mock(),
                 'ASH_START': 'start', 'BEACON_REMAIN': 'remain'}
        exec(compile(tree, str(path), 'exec'), scope)
        instance = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                                   handle_map_event=Mock(return_value=False),
                                   appear=Mock(side_effect=[True, False]),
                                   digit_ocr_point_and_check=Mock(return_value=1),
                                   _ensure_meta_level=Mock(), _make_an_attack=Mock())
        self.assertFalse(scope['_attack_meta'](instance))
        instance._make_an_attack.assert_called_once()
        timer.reset.assert_called_once()
