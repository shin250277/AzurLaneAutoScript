"""Campaign slot isolation using synthetic data; no account/device access."""
import subprocess
import sys
import unittest


class CampaignSlotTest(unittest.TestCase):
    def test_three_slots_bind_and_modify_only_the_selected_slot(self):
        code = '''
from copy import deepcopy
from unittest.mock import patch
from module.config.config import AzurLaneConfig
data = {name: {
    'Campaign': {'Name': str(index), 'Event': 'campaign_main', 'Mode': 'normal'},
    'Scheduler': {'Enable': False, 'Command': name, 'NextRun': 'synthetic'},
    'StopCondition': {'RunCount': index}
} for index, name in enumerate(('Main', 'Main2', 'Main3'), 1)}
original = deepcopy(data)
with patch.object(AzurLaneConfig, 'update', side_effect=AssertionError('No file writes')):
    config = object.__new__(AzurLaneConfig)
    config.bound = {}
    config.auto_update = False
    config.modified = {}
    config.overridden = {}
    config.data = data
    for index, name in enumerate(('Main', 'Main2', 'Main3'), 1):
        config.bind(name)
        assert config.Campaign_Name == str(index)
        assert config.StopCondition_RunCount == index
        config.StopCondition_RunCount = 0
        assert config.modified[name + '.StopCondition.RunCount'] == 0
        assert config.bound['Scheduler_Enable'] == name + '.Scheduler.Enable'
    assert set(config.modified) == {name + '.StopCondition.RunCount' for name in data}
    assert data == original
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
