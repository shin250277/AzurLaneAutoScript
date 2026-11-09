from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from module.map.kr_preparation import preparation_button, KR_MAP_PREPARATION
from dev_tools.test_os_task_stop_boundaries import method


class EventCancelTest(TestCase):
    def test_localized_preparation_closes_without_sortie(self):
        close = method('module/map/map_operation.py', 'MapOperation', 'enter_map_cancel',
                       preparation_button=preparation_button, MAP_PREPARATION='old',
                       MAP_PREPARATION_HARD='hard', FLEET_PREPARATION='fleet',
                       MAP_PREPARATION_CANCEL='old_close')
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                             is_in_stage=Mock(side_effect=[False, True]),
                             appear=Mock(side_effect=lambda button, **kw: button is KR_MAP_PREPARATION))
        self.assertTrue(close(ui))
        ui.device.click.assert_called_once()
        self.assertEqual(ui.device.click.call_args[0][0].name, 'KR_PREPARATION_CLOSE')

    def test_already_in_stage_does_not_click(self):
        close = method('module/map/map_operation.py', 'MapOperation', 'enter_map_cancel')
        ui = SimpleNamespace(device=Mock(), is_in_stage=Mock(return_value=True))
        self.assertTrue(close(ui))
        ui.device.click.assert_not_called()
