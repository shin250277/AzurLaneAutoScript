"""Oil cap is a deferred task, not repeated clicks or automatic food buying."""
import subprocess
import sys
import unittest


class KoreanCommissionOilMaxedTest(unittest.TestCase):
    def test_notice_checked_before_receiving_and_deferred_without_purchase(self):
        code = '''
from unittest.mock import Mock, MagicMock, patch
from module.commission.commission import RewardCommission
from module.exception import OilMaxed
class TaskEnd(Exception):
    pass
ui = Mock()
ui.config.SERVER = 'kr'
ui.stat.new.return_value = MagicMock()
ui.appear.return_value = True
try:
    RewardCommission._commission_receive(ui)
except OilMaxed:
    pass
else:
    raise AssertionError('Oil notice not handled')
ui.appear_then_click.assert_not_called()
ui.device.click.assert_not_called()
ui._commission_receive.side_effect = OilMaxed
ui.config.task_stop.side_effect = TaskEnd
with patch('module.commission.commission.RewardDorm') as dorm:
    try:
        RewardCommission.commission_receive(ui)
    except TaskEnd:
        pass
    else:
        raise AssertionError('Task not deferred')
    dorm.assert_not_called()
ui.config.task_delay.assert_called_once_with(minute=30)
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
