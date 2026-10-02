"""Do not click the main menu while the island scene is still loading."""
import subprocess
import sys
import unittest


class IslandLoadingTest(unittest.TestCase):
    def test_confirmed_source_menu_retries_only_once(self):
        code = '''
from unittest.mock import Mock, patch
from module.ui.ui import UI
from module.ui.assets import DORMMENU_GOTO_ISLAND, ISLAND_CHECK
from module.exception import RequestHumanTakeover
ui = Mock()
ui.appear.side_effect = [False, True, True]
with patch('module.ui.ui.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    UI.wait_kr_island_scene(ui)
ui.device.click.assert_called_once_with(DORMMENU_GOTO_ISLAND)
ui.device.image_save.assert_not_called()
ui = Mock()
ui.appear.side_effect = lambda button, **kwargs: button != ISLAND_CHECK
with patch('module.ui.ui.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    try:
        UI.wait_kr_island_scene(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Must not retry unchanged source menu indefinitely')
ui.device.click.assert_called_once_with(DORMMENU_GOTO_ISLAND)
ui.device.image_save.assert_called_once()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_scene_ready_and_timeout_never_click(self):
        code = '''
from unittest.mock import Mock, patch
from module.ui.ui import UI
from module.exception import RequestHumanTakeover
ui = Mock()
ui.appear.return_value = True
with patch('module.ui.ui.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = False
    UI.wait_kr_island_scene(ui)
ui.device.screenshot.assert_called_once_with()
ui.device.click.assert_not_called()
ui.reset_mock()
ui.appear.return_value = False
with patch('module.ui.ui.Timer') as timer:
    timer.return_value.start.return_value.reached.return_value = True
    try:
        UI.wait_kr_island_scene(ui)
    except RequestHumanTakeover:
        pass
    else:
        raise AssertionError('Unknown loading screen must stop, not resume clicking')
ui.device.image_save.assert_called_once_with('./log/kr_island_loading_timeout.png')
ui.device.click.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
