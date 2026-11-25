"""Collect-only construction must never enter the spending path."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class CollectOnlyTest(unittest.TestCase):
    def test_gui_schema_exposes_zero_and_preserves_default(self):
        import yaml
        source = yaml.safe_load(Path('module/config/argument/argument.yaml').read_text(encoding='utf-8'))
        generated = json.loads(Path('module/config/argument/args.json').read_text(encoding='utf-8'))
        for option in (source['Gacha']['Amount'], generated['Gacha']['Gacha']['Amount']):
            self.assertIn(0, option['option'])
            self.assertEqual(option['value'], 1)

    def test_zero_collects_without_resource_scan_or_submission(self):
        path = Path('module/gacha/gacha_reward.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'RewardGacha')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'gacha_run')]
        scope = {'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        ui = Mock()
        ui.config = SimpleNamespace(Gacha_Amount=0)
        self.assertTrue(scope['gacha_run'](ui))
        ui.ui_goto_gacha.assert_called_once_with()
        ui.gacha_flush_queue.assert_called_once_with(collect_only=True)
        ui.gacha_goto_pool.assert_not_called()
        ui.gacha_prep.assert_not_called()
        ui.gacha_submit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
