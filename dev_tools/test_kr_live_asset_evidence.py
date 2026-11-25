import unittest

from dev_tools.kr_live_asset_evidence import completed_clicks


class LiveControlEvidenceTest(unittest.TestCase):
    def test_only_balanced_clean_kr_tasks(self):
        parts = ['[Server] cn', 'Scheduler: Start task `A`', '| INFO | Click ( 1, 2) @ OTHER',
                 'Scheduler: End task `A`', '[Server] kr', 'Scheduler: Start task `A`',
                 '| INFO | Click ( 1, 2) @ FAILED', '| ERROR | Stuck', 'Scheduler: End task `A`',
                 'Scheduler: Start task `A`', '| INFO | Click ( 1, 2) @ GOOD',
                 '| INFO | Click ( 1, 2) @ GOOD', 'Scheduler: End task `A`',
                 'Scheduler: Start task `B`', '| INFO | Click ( 1, 2) @ UNFINISHED']
        self.assertEqual(list(completed_clicks(parts)), ['GOOD'])
