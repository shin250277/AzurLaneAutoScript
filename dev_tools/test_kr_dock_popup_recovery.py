"""Page recovery may dismiss a dock-full warning, never expand or retire."""
import subprocess
import sys
import unittest


class KoreanDockPopupRecoveryTest(unittest.TestCase):
    def test_real_recovery_closes_only_identified_kr_warning(self):
        code = '''
from unittest.mock import Mock
import numpy as np
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.ui.ui import UI, KR_DOCK_FULL_CLOSE
button = KR_DOCK_FULL_CLOSE
assert button.button == (865, 177, 925, 215)
assert button.match(np.array(Image.open(button.file).convert('RGB')))
assert not button.match(np.zeros((720, 1280, 3), dtype=np.uint8))
ui = Mock()
ui.appear.return_value = True
assert UI.ui_close_kr_dock_full(ui)
ui.device.click.assert_called_once_with(button)
ui.reset_mock()
ui.appear.return_value = False
assert not UI.ui_close_kr_dock_full(ui)
ui.device.click.assert_not_called()
ui.reset_mock()
server.server = 'jp'
assert not UI.ui_close_kr_dock_full(ui)
ui.appear.assert_not_called()
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], timeout=30,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    unittest.main()
