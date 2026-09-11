import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class KrHardBossTest(unittest.TestCase):
    def test_only_detected_kr_boss_uses_hard_boss_handler(self):
        path = Path('campaign/campaign_hard/campaign_hard.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Campaign')
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'battle_default']
        tree.body = [cls]
        class Base:
            def battle_default(self):
                return 'ordinary'
        scope = {'CampaignBase': Base}
        exec(compile(tree, str(path), 'exec'), scope)
        for server, boss, expected in [('kr', True, 'boss'), ('kr', False, 'ordinary'), ('jp', True, 'ordinary')]:
            instance = scope['Campaign']()
            instance.config = SimpleNamespace(SERVER=server)
            instance.map = SimpleNamespace(select=Mock(return_value=boss))
            instance.clear_boss = Mock(return_value='boss')
            self.assertEqual(instance.battle_default(), expected)
            self.assertEqual(instance.clear_boss.call_count, int(expected == 'boss'))
