"""Exercise real imports so mocked guard tests cannot hide missing exceptions."""
import subprocess
import sys
import unittest


class FreebiesImportTest(unittest.TestCase):
    def test_kr_freebies_import_and_real_confirmation_exception(self):
        code = '''
from unittest.mock import Mock
import module.config.server as server
server.server = 'kr'
from module.freebies.freebies import Freebies
from module.freebies.supply_pack import SupplyPack, BUY_CONFIRM, FREE_SUPPLY_PACK
from module.exception import RequestHumanTakeover
ui = Mock()
ui.appear.side_effect = lambda button, **kwargs: button is BUY_CONFIRM
try:
    SupplyPack.supply_pack_buy(ui, FREE_SUPPLY_PACK)
except RequestHumanTakeover:
    pass
else:
    raise AssertionError('Unselected purchase confirmation was not rejected')
ui.device.click.assert_not_called()
ui.appear_then_click.assert_not_called()
ui.handle_popup_confirm.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    unittest.main()
