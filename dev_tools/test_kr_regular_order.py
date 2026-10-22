"""KR regular orders require a quota transition, never timer-only success."""
import subprocess
import sys
import unittest


class KoreanRegularOrderTest(unittest.TestCase):
    def test_empty_portraits_with_remaining_quota_never_reports_completion(self):
        self.run_code('''
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island.korean_order import run_regular_orders
ui = Mock()
ui.config.cross_get.return_value = None
ui.loop.return_value = iter(range(3))
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
ui.regular_orders = ui.regular_cooldown_orders = ui.urgent_orders = ui.season_orders = []
with patch('module.island.korean_order.read_quota', return_value=14):
    try:
        run_regular_orders(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Empty detection with remaining quota is not completion')
ui.config.task_delay.assert_not_called()
ui.device.click.assert_not_called()
ui.config.cross_set.assert_not_called()
''')

    def test_transient_quota_overlay_recovers_without_submitting(self):
        self.run_code('''
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island.korean_order import read_order_quota
ui = Mock()
ui.loop.return_value = iter(range(3))
ui.handle_island_additional.side_effect = [True, False, False]
ui.handle_island_order_level_up.return_value = False
with patch('module.island.korean_order.read_quota', side_effect=[None, None, 14]):
    assert read_order_quota(ui) == 14
ui.device.click.assert_not_called()
ui.config.cross_set.assert_not_called()
ui.handle_island_additional.side_effect = None
ui.handle_island_additional.return_value = False
ui.loop.return_value = iter(range(2))
with patch('module.island.korean_order.read_quota', return_value=None):
    try:
        read_order_quota(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Persistent unreadable quota must stop')
ui.device.click.assert_not_called()
''')

    def test_adjacent_cooldown_orders_are_all_removed(self):
        self.run_code('''
from unittest.mock import Mock
from module.island.order import IslandOrder
ui = Mock()
first = Mock(button=(10, 100, 30, 120))
second = Mock(button=(50, 100, 70, 120))
ready = Mock(button=(90, 100, 110, 120))
original = [first, second, ready]
ui.detect_orders.side_effect = [[first, second], original, [], []]
IslandOrder.detect_all_orders(ui)
assert ui.regular_orders == [ready], 'Consecutive cooldown orders must not be skipped'
assert original == [first, second, ready], 'Do not mutate detection results in place'
ui.device.click.assert_not_called()
''')

    def test_top_map_portrait_uses_center_not_header_or_panel(self):
        self.run_code('''
from module.base.button import Button
from module.island.korean_order import safe_order_target
order = Button(area=(748, 28, 852, 132), color=(), button=(756, 36, 844, 124), name='Lisa')
target = safe_order_target(order)
assert target.button == (792, 72, 808, 88)
for box in ((900, 600, 1200, 680), (10, 0, 98, 60), (0, 680, 88, 720)):
    assert safe_order_target(Button(area=box, color=(), button=box, name='unsafe')) is None
''')

    def test_runner_only_uses_regular_orders_and_preserves_other_work(self):
        self.run_code('''
from unittest.mock import Mock, patch
from module.island.korean_order import run_regular_orders
ui = Mock()
ui.config.cross_get.return_value = None
order = Mock(button=(20, 200, 100, 280))
outside = Mock(button=(900, 600, 1200, 680))
ui.regular_orders = [outside, order]
ui.urgent_orders = [Mock()]
ui.season_orders = [Mock()]
ui.loop.return_value = iter(range(3))
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
with patch('module.island.korean_order.submit_regular', return_value=False) as submit:
    run_regular_orders(ui)
    submit.assert_called_once_with(ui)
assert ui.click_order.call_count == 1
assert ui.click_order.call_args[0][0].button == (52, 232, 68, 248)
ui.reject_order.assert_not_called()
ui.update_stuck_season_order.assert_not_called()
ui.config.cross_set.assert_not_called()
ui.config.task_delay.assert_called_once_with(minute=30, server_update=True)
''')

    def run_code(self, code):
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_strict_quota(self):
        self.run_code('''
from module.island.korean_order import parse_quota
assert parse_quota('15/15') == 15
assert parse_quota('14/15') == 14
assert parse_quota('0/15') == 0
for value in ('115/15', '14/150', '14', '', 'x14/15', None):
    assert parse_quota(value) is None
''')

    def test_submission_requires_two_confirming_frames_and_keeps_uncertainty(self):
        self.run_code('''
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island.korean_order import submit_regular, PENDING_KEY
ui = Mock()
ui.config.SERVER = 'kr'
ui.config.cross_get.return_value = None
ui.scan_current_order_requirements.return_value = {2703: (43, 6, 37)}
ui.is_order_satisfied.return_value = True
ui.match_template_color.return_value = True
ui.handle_island_additional.return_value = False
ui.handle_island_order_level_up.return_value = False
ui.loop.return_value = iter(range(4))
with patch('module.island.korean_order.read_quota', side_effect=[15, 15, 14, 14]):
    assert submit_regular(ui) is True
assert ui.device.click.call_count == 1
ui.config.update.assert_called_once_with()
assert ui.config.cross_set.call_args_list[-1][0] == (PENDING_KEY, None)
ui.reset_mock()
ui.loop.return_value = iter(range(3))
with patch('module.island.korean_order.read_quota', return_value=15):
    try:
        submit_regular(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Unchanged quota reported as success')
assert ui.device.click.call_count == 1
assert ui.config.cross_set.call_count == 1
assert ui.config.cross_set.call_args[0][1]['quota'] == 15
ui.reject_order.assert_not_called()
''')

    def test_changed_requirements_disabled_button_and_pending_never_click(self):
        self.run_code('''
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island.korean_order import submit_regular
for case in ('pending', 'changed', 'disabled', 'insufficient'):
    ui = Mock()
    ui.config.SERVER = 'kr'
    ui.config.cross_get.return_value = {'quota': 15} if case == 'pending' else None
    ui.scan_current_order_requirements.side_effect = [
        {2703: (43, 6, 37)}, {2703: (42, 6, 36)} if case == 'changed' else {2703: (43, 6, 37)}]
    ui.is_order_satisfied.return_value = case != 'insufficient'
    ui.match_template_color.return_value = case != 'disabled'
    with patch('module.island.korean_order.read_quota', return_value=15):
        try:
            submit_regular(ui)
        except RequestHumanTakeover:
            pass
    ui.device.click.assert_not_called()
    ui.config.cross_set.assert_not_called()
''')
