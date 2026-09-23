"""Offline checks for the observed Korean Bigshot raid labels."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class KrBigshotAssetsTest(unittest.TestCase):
    def test_fleet_recovery_requires_both_header_and_close(self):
        recover = method('module/ui/ui.py', 'UI', '_handle_kr_raid_fleet_back',
                         BIGSHOT_FLEET_HEADER='header', BIGSHOT_FLEET_CLOSE='close')
        for detected in ([False], [True, False], [True, True]):
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.appear.side_effect = detected
            self.assertEqual(recover(ui), all(detected))
            self.assertEqual(ui.device.click.call_count, int(all(detected)))

    def test_unprepared_kr_fleet_stops_without_restart_or_click(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.appear.return_value = False
        ui.appear_then_click.return_value = False
        ui.combat_appear.return_value = False
        ui.device.screenshot.side_effect = RuntimeError('Unbounded preparation wait')
        timer = Mock()
        timer.return_value.start.return_value.reached.return_value = True
        enter = method('module/raid/raid.py', 'Raid', 'raid_enter',
                       Timer=timer, raid_entrance=Mock(return_value='entrance'),
                       RAID_FLEET_PREPARATION='preparation')
        with self.assertRaises(TaskStopped):
            enter(ui, 'hard', 'raid_20260827')
        ui.device.click.assert_not_called()
        ui.appear_then_click.assert_not_called()
        ui.device.image_save.assert_called_once_with('./log/kr_raid_preparation_timeout.png')

    def test_local_labels_and_negative_frame(self):
        code = """
import numpy as np
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.ui.page import page_raid
from module.ui.assets import RAID_CHECK_20260827
from module.raid.raid import raid_entrance
from module.raid.assets import RAID_FLEET_PREPARATION
from module.raid.kr_fleet import BIGSHOT_FLEET_HEADER, BIGSHOT_FLEET_CLOSE
buttons = [RAID_CHECK_20260827] + [raid_entrance('raid_20260827', mode)
                                  for mode in ('easy', 'normal', 'hard')]
buttons.extend([BIGSHOT_FLEET_HEADER, BIGSHOT_FLEET_CLOSE, RAID_FLEET_PREPARATION])
for button in buttons:
    assert '/kr/' in button.file.replace('\\\\', '/'), button.file
    frame = np.array(Image.open(button.file).convert('RGB'))
    assert button.match(frame), button.name
    assert not button.match(np.zeros((720, 1280, 3), dtype=np.uint8)), button.name
"""
        result = subprocess.run([sys.executable, '-c', code],
                                cwd=str(Path(__file__).resolve().parents[1]),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    unittest.main()
