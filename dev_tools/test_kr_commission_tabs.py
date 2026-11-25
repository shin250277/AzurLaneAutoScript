"""KR selector input must stay inside labels, away from back navigation."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class CommissionTabsTest(unittest.TestCase):
    def test_tab_hitboxes_are_inside_observed_labels(self):
        tree = ast.parse(Path('module/commission/commission.py').read_text(encoding='utf-8'))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'add_state'
                 and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == 'KR_COMMISSION_SWITCH']
        boxes = []
        for call in calls:
            button = next(k.value for k in call.keywords if k.arg == 'click_button')
            boxes.append(next(ast.literal_eval(k.value) for k in button.keywords if k.arg == 'button'))
        self.assertEqual(boxes, [(35, 145, 70, 180), (35, 240, 70, 275)])

    def test_only_kr_uses_safe_selector(self):
        original, korean = Mock(), Mock()
        original.set.return_value = korean.set.return_value = False
        run = method('module/commission/commission.py', 'RewardCommission',
                     '_commission_ensure_mode', COMMISSION_SWITCH=original,
                     KR_COMMISSION_SWITCH=korean)
        ui = Mock()
        for region in ('kr', 'cn', 'jp', 'en', 'tw'):
            ui.config.SERVER = region
            self.assertFalse(run(ui, 'daily'))
        self.assertEqual(korean.set.call_count, 1)
        self.assertEqual(original.set.call_count, 4)


if __name__ == '__main__':
    unittest.main()
