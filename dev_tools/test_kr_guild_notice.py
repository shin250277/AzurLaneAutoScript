"""A guild completion notice may be dismissed, never followed to the guild."""
import subprocess
import sys
import unittest


class GuildNoticeTest(unittest.TestCase):
    def test_close_only_localized_completion_notice(self):
        code = '''
from unittest.mock import Mock
import numpy as np
from PIL import Image
from module.handler.info_handler import InfoHandler, KR_GUILD_NOTICE_CLOSE
button = KR_GUILD_NOTICE_CLOSE
assert button.button == (440, 452, 607, 482)
assert button.match(np.array(Image.open(button.file).convert('RGB')))
assert not button.match(np.zeros((720, 1280, 3), dtype=np.uint8))
ui = Mock()
ui.config.SERVER = 'kr'
ui.appear.side_effect = lambda item, **kwargs: item == button
assert InfoHandler.handle_guild_popup_cancel(ui)
ui.device.click.assert_called_once_with(button)
ui.reset_mock()
ui.appear.side_effect = None
ui.appear.return_value = False
assert not InfoHandler.handle_guild_popup_cancel(ui)
ui.device.click.assert_not_called()
ui.config.SERVER = 'jp'
ui.reset_mock()
ui.appear.side_effect = lambda item, **kwargs: item == button
assert not InfoHandler.handle_guild_popup_cancel(ui)
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
