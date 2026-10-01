"""KR META recovery must share the normal page-navigation cooldown."""
import subprocess
import sys
import unittest


class MetaNavigationTest(unittest.TestCase):
    def test_localized_recovery_and_home_cooldown(self):
        code = '''
from unittest.mock import Mock
from module.ui.ui import UI, GOTO_MAIN, KR_META_CHECK
from module.ui.page import page_meta
ui = Mock()
ui.config.SERVER = 'kr'
ui.ui_page_appear.return_value = False
assert not UI.ui_handle_meta_return(ui)
ui.appear_then_click.assert_not_called()
ui.ui_page_appear.assert_called_once_with(page_meta, offset=(30, 30), interval=5)
ui.ui_page_appear.return_value = True
ui.appear_then_click.return_value = True
assert UI.ui_handle_meta_return(ui)
ui.appear_then_click.assert_called_once_with(GOTO_MAIN, offset=(30, 30), interval=2)
UI.ui_button_interval_reset(ui, GOTO_MAIN)
ui.interval_reset.assert_any_call(GOTO_MAIN)
ui.interval_reset.assert_any_call(KR_META_CHECK)
ui.reset_mock()
ui.config.SERVER = 'jp'
ui.appear.return_value = True
assert UI.ui_handle_meta_return(ui)
ui.ui_page_appear.assert_not_called()
ui.appear_then_click.assert_called_once_with(GOTO_MAIN, offset=(30, 30))
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
