"""Fresh-process KR imports and real method dispatch, with no device creation."""
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


class KrOsImportTest(unittest.TestCase):
    def test_production_imports_and_failure_paths_without_device(self):
        code = textwrap.dedent('''
            from unittest.mock import Mock, patch
            import module.config.server as server
            server.server = 'kr'
            with patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
                from module.os.operation_siren import OperationSiren
                from module.campaign.os_run import OSCampaignRun
                from module.os.tasks.stronghold import OpsiStronghold
                from module.os.tasks.month_boss import OpsiMonthBoss
                from module.os_handler.action_point import ActionPointHandler
                from module.exception import RequestHumanTakeover

                assert OperationSiren.clear_stronghold is OpsiStronghold.clear_stronghold
                assert OperationSiren.clear_month_boss is OpsiMonthBoss.clear_month_boss
                assert OperationSiren.action_point_buy is ActionPointHandler.action_point_buy
                assert callable(OSCampaignRun.opsi_month_boss)

                ui = Mock()
                ui.config.SERVER = 'kr'
                ui.action_point_set_button.return_value = False
                try:
                    OperationSiren.action_point_buy(ui)
                except RequestHumanTakeover:
                    pass
                else:
                    raise AssertionError('Unconfirmed oil selection was allowed')
                ui.action_point_use.assert_not_called()
                ui.action_point_get_buy_remain.assert_not_called()

                ui = Mock()
                ui.run_stronghold.return_value = False
                try:
                    OperationSiren.clear_stronghold(ui)
                except RequestHumanTakeover:
                    pass
                else:
                    raise AssertionError('Failed stronghold returned normally')
                ui.fleet_repair.assert_not_called()
            print('KR_OS_IMPORT_OK')
        ''')
        result = subprocess.run([sys.executable, '-c', code],
                                cwd=str(Path(__file__).resolve().parents[1]),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=30)
        output = result.stdout.decode('utf-8', errors='replace')
        self.assertEqual(result.returncode, 0, output)
        self.assertIn('KR_OS_IMPORT_OK', output)


if __name__ == '__main__':
    unittest.main()
