"""Regression checks for the Korean meow acquisition screen."""
import subprocess
import sys
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class MeowGetTest(unittest.TestCase):
    def test_resume_queue_closes_modal_before_navigation(self):
        run = method('module/meowfficer/meowfficer.py', 'RewardMeowfficer', 'run',
                     page_meowfficer='page', MEOWFFICER_GET_CHECK='get',
                     MEOWFFICER_TRAIN_FILL_QUEUE='fill')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.Meowfficer_BuyAmount = 1
        ui.config.Meowfficer_OverflowCoins = -1
        ui.config.MeowfficerTrain_Enable = False
        ui.appear.side_effect = lambda button, **kw: button == 'fill'
        run(ui)
        ui.meow_menu_close.assert_called_once_with()
        calls = [c[0] for c in ui.mock_calls]
        self.assertLess(calls.index('meow_menu_close'), calls.index('ui_ensure'))

    def test_acquisition_can_return_to_kr_main(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.appear.side_effect = lambda button, **kw: button == 'enter'
        ui.handle_meow_popup_dismiss.return_value = False
        ui._handle_meow_train_evaluate.return_value = False
        ui.device.screenshot.side_effect = RuntimeError('Unbounded acquisition wait')
        get = method('module/meowfficer/collect.py', 'MeowfficerCollect', 'meow_get',
                     Timer=Mock(), MEOWFFICER_TRAIN_START='start',
                     MEOWFFICER_TRAIN_ENTER='enter', MEOWFFICER_GET_CHECK='get')
        get(ui)
        ui.device.click.assert_not_called()

    def test_reenter_training_after_kr_collect(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.MeowfficerTrain_Mode = 'once_a_day'
        capacity = Mock()
        capacity.ocr.return_value = (96, 24, 120)
        train = method('module/meowfficer/train.py', 'MeowfficerTrain', 'meow_train',
                       MEOWFFICER_CAPACITY=capacity, MEOWFFICER_BOX_COUNT=Mock(),
                       MEOWFFICER_TRAIN_ENTER='enter', MEOWFFICER_TRAIN_START='start')
        train(ui)
        self.assertEqual(ui.meow_enter.call_count, 2)

    def test_kr_queue_failure_is_not_success(self):
        enter = method('module/meowfficer/train.py', 'MeowfficerTrain', '_meow_queue_enter',
                       MEOWFFICER_TRAIN_FILL_QUEUE='fill', MEOWFFICER_TRAIN_START='start')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.appear.side_effect = lambda button, **kw: button == 'start'
        ui.info_bar_count.return_value = 0
        with self.assertRaises(TaskStopped):
            enter(ui)
        self.assertEqual(ui.device.click.call_count, 3)
        ui.device.image_save.assert_called_once()

    def test_korean_acquisition_asset(self):
        code = """
import numpy as np
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.meowfficer.assets import MEOWFFICER_GET_CHECK as button
assert '/kr/' in button.file.replace('\\\\', '/')
frame = np.array(Image.open(button.file).convert('RGB'))
assert button.match(frame)
assert not button.match(np.zeros((720, 1280, 3), dtype=np.uint8))
from module.meowfficer.assets import MEOWFFICER_TRAIN_FILL_QUEUE as button
assert '/kr/' in button.file.replace('\\\\', '/')
assert button.match(np.array(Image.open(button.file).convert('RGB')))
assert not button.match(np.zeros((720, 1280, 3), dtype=np.uint8))
"""
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_resume_acquisition_before_navigation(self):
        run = method('module/meowfficer/meowfficer.py', 'RewardMeowfficer', 'run',
                     page_meowfficer='page', MEOWFFICER_GET_CHECK='get',
                     MEOWFFICER_TRAIN_FILL_QUEUE='fill')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.Meowfficer_BuyAmount = 1
        ui.config.Meowfficer_OverflowCoins = -1
        ui.config.Meowfficer_FortChoreMeowfficer = False
        ui.config.MeowfficerTrain_Enable = False
        ui.appear.return_value = True
        run(ui)
        ui.meow_get.assert_called_once_with()
        calls = [c[0] for c in ui.mock_calls]
        self.assertLess(calls.index('meow_get'), calls.index('ui_ensure'))
