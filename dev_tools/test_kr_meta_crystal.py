"""Crystal rewards require two independent public UI anchors, never artwork."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
import numpy as np


class CrystalCardTest(unittest.TestCase):
    def handler(self):
        tree = ast.parse(Path('module/meta_reward/meta_reward.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'handle_kr_crystal_card')
        tree.body = [method]
        scope = dict(KR_CRYSTAL_LABEL='label', KR_CRYSTAL_COMMENT='comment')
        exec(compile(tree, 'crystal', 'exec'), scope)
        return scope['handle_kr_crystal_card']

    def test_only_two_anchors_allow_dismiss(self):
        for region, anchors, expected in [('kr', [True, True], True),
                                          ('kr', [False], False),
                                          ('kr', [True, False], False),
                                          ('jp', [], False)]:
            ui = SimpleNamespace(config=SimpleNamespace(SERVER=region),
                                 match_template_color=Mock(side_effect=anchors), device=Mock())
            self.assertEqual(self.handler()(ui), expected)
            self.assertEqual(ui.device.click.call_count, int(expected))
            if expected:
                ui.device.click.assert_called_once_with('label')

    def test_public_asset_positive_blank_and_partial_negative(self):
        from module.base.button import Button
        from module.base.utils import load_image
        tree = ast.parse(Path('module/meta_reward/meta_reward.py').read_text(encoding='utf-8'))
        buttons = []
        for name in ('KR_CRYSTAL_LABEL', 'KR_CRYSTAL_COMMENT'):
            node = next(n for n in tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
            buttons.append(Button(**{k.arg: ast.literal_eval(k.value) for k in node.value.keywords}))
        public = load_image('assets/kr/meta_reward/KR_CRYSTAL_CARD.png')
        blank = np.zeros_like(public)
        for button in buttons:
            self.assertTrue(button.match_template_color(public, offset=(3, 3)))
            self.assertFalse(button.match_template_color(blank, offset=(3, 3)))
        partial = public.copy()
        partial[465:510, 42:83] = 0
        self.assertTrue(buttons[0].match_template_color(partial, offset=(3, 3)))
        self.assertFalse(buttons[1].match_template_color(partial, offset=(3, 3)))
