"""Tactical reward entry must identify the card, never just orange pixels."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class TacticalEntryTest(unittest.TestCase):
    def setUp(self):
        self.card = SimpleNamespace(button=(402, 395, 528, 435))
        self.run_entry = method('module/tactical/tactical_class.py', 'RewardTacticalClass',
                                '_handle_kr_tactical_reward_entry',
                                KR_TACTICAL_REWARD_CARD=self.card)
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  appear=Mock(return_value=True),
                                  image_color_count=Mock(return_value=True),
                                  device=SimpleNamespace(click=Mock()))

    def test_missing_title_or_cooldown_never_clicks(self):
        self.ui.appear.return_value = False
        self.assertFalse(self.run_entry(self.ui))
        self.ui.device.click.assert_not_called()
        self.ui.image_color_count.assert_not_called()

    def test_title_without_button_never_clicks(self):
        self.ui.image_color_count.return_value = False
        self.assertFalse(self.run_entry(self.ui))
        self.ui.device.click.assert_not_called()

    def test_title_and_button_click_once_with_cooldown(self):
        self.assertTrue(self.run_entry(self.ui))
        self.ui.appear.assert_called_once_with(self.card, offset=(20, 150), interval=3)
        self.ui.device.click.assert_called_once_with(self.card)
        self.assertEqual(self.ui.image_color_count.call_args_list[0][0][0], self.card.button)

    def test_non_kr_unchanged(self):
        self.ui.config.SERVER = 'jp'
        self.assertFalse(self.run_entry(self.ui))
        self.ui.appear.assert_not_called()

    def test_legacy_reward_buttons_cannot_bypass_kr_guard(self):
        tree = ast.parse(Path('module/tactical/tactical_class.py').read_text(encoding='utf-8'))
        names = {'REWARD_2', 'REWARD_2_WHITE', 'REWARD_GOTO_TACTICAL',
                 'REWARD_GOTO_TACTICAL_WHITE'}
        found = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            calls = [n for n in ast.walk(node.test) if isinstance(n, ast.Call)]
            for call in calls:
                if call.args and isinstance(call.args[0], ast.Name) and call.args[0].id in names:
                    if isinstance(call.func, ast.Attribute) and call.func.attr == 'appear_then_click':
                        found.add(call.args[0].id)
                        self.assertIsInstance(node.test, ast.BoolOp)
                        guard = node.test.values[0]
                        self.assertIsInstance(guard, ast.Compare)
                        self.assertIsInstance(guard.ops[0], ast.NotEq)
                        self.assertEqual(guard.comparators[0].s, 'kr')
        self.assertEqual(found, names)


if __name__ == '__main__':
    unittest.main()
