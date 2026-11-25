"""KR submission must not repeat consumption or infer success from a timer."""
import subprocess
import sys
import unittest


class OrderSubmissionTest(unittest.TestCase):
    def test_confirmed_transition_and_legacy_behavior(self):
        code = '''
from unittest.mock import Mock, patch
from module.island.order import IslandOrder, ISLAND_ORDER_ACCEPT, ISLAND_ORDER_BACKGROUND
ui = Mock()
ui.config.SERVER = 'kr'
ui.loop.return_value = iter(range(8))
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
ui.match_template_color.side_effect = lambda b, **kw: b == (ISLAND_ORDER_BACKGROUND if ui.device.click.called else ISLAND_ORDER_ACCEPT)
with patch('module.island.order.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    assert IslandOrder.submit_order(ui) is True
ui.device.click.assert_called_once_with(ISLAND_ORDER_ACCEPT)
ui.reset_mock()
ui.config.SERVER = 'jp'
ui.loop.return_value = iter(range(8))
ui.match_template_color.side_effect = lambda b, **kw: b == ISLAND_ORDER_BACKGROUND
with patch('module.island.order.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    assert IslandOrder.submit_order(ui) is True
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_single_click_and_no_timeout_success(self):
        code = '''
from unittest.mock import Mock, patch
from module.island.order import IslandOrder, ISLAND_ORDER_ACCEPT
ui = Mock()
ui.config.SERVER = 'kr'
ui.loop.return_value = iter(range(8))
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
ui.match_template_color.side_effect = lambda b, **kw: b == ISLAND_ORDER_ACCEPT
with patch('module.island.order.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    result = IslandOrder.submit_order(ui)
assert result is False
assert ui.device.click.call_count == 1, ui.device.click.call_count
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_background_without_submission_is_not_success(self):
        code = '''
from unittest.mock import Mock, patch
from module.island.order import IslandOrder, ISLAND_ORDER_BACKGROUND
ui = Mock()
ui.config.SERVER = 'kr'
ui.loop.return_value = iter(range(8))
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
ui.match_template_color.side_effect = lambda b, **kw: b == ISLAND_ORDER_BACKGROUND
with patch('module.island.order.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    result = IslandOrder.submit_order(ui)
assert result is False
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
