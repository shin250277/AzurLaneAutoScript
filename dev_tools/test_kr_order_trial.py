import tempfile
from pathlib import Path
import unittest
import subprocess
import sys


class OrderTrialTest(unittest.TestCase):
    def test_runtime_receipt_and_disabled_button(self):
        code = '''
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from module.exception import RequestHumanTakeover
from module.island.order_trial import run_trial
with TemporaryDirectory() as directory:
    receipt = Path(directory) / 'attempt.json'
    ui = Mock()
    ui.config.SERVER = 'kr'
    ui.regular_orders = [Mock(button=(30, 200, 110, 280))]
    ui.scan_current_order_requirements.return_value = {2703: (43, 6, 37)}
    ui.is_order_satisfied.return_value = True
    ui.match_template_color.return_value = False
    with patch('module.island.order_trial.RECEIPT', receipt):
        try:
            run_trial(ui)
        except RequestHumanTakeover:
            pass
        else:
            raise AssertionError('Disabled submit accepted')
        assert not receipt.exists()
        ui.device.click.assert_not_called()
        ui.match_template_color.return_value = True
        ui.loop.return_value = iter([])
        run_trial(ui)
        assert receipt.exists()
        assert ui.device.click.call_count == 1
        try:
            run_trial(ui)
        except RequestHumanTakeover:
            pass
        else:
            raise AssertionError('Repeated attempt accepted')
        assert ui.device.click.call_count == 1
        ui.reject_order.assert_not_called()
        ui.config.cross_set.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_exact_single_item_cost(self):
        from module.island.order_trial import validate_requirements
        self.assertTrue(validate_requirements({2703: (43, 6, 37)}))
        for value in [{}, {2703: (5, 6, -1)}, {2703: (43, 7, 36)},
                      {2703: (43, 6, 38)}, {2702: (43, 6, 37)},
                      {2703: (43, 6, 37), 2601: (519, 8, 511)}]:
            self.assertFalse(validate_requirements(value))

    def test_attempt_cannot_be_repeated(self):
        from module.island.order_trial import reserve_attempt
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'attempt.json'
            reserve_attempt(target, {2703: (43, 6, 37)})
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                reserve_attempt(target, {2703: (43, 6, 37)})
            self.assertEqual(before, target.read_bytes())
