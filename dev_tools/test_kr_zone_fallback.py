"""Do not repeatedly run a Hangul-incompatible OCR before the globe fallback."""
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class MapNameFailure(Exception):
    pass


class KoreanZoneFallbackTest(unittest.TestCase):
    def test_two_failed_reads_use_globe_without_exhausting_retry_loop(self):
        timer = Mock()
        timer.start.return_value.reached.return_value = False
        zone_init = method('module/os/map_operation.py', 'OSMapOperation', 'zone_init',
                           Timer=Mock(return_value=timer), AUTO_SEARCH_REWARD='reward',
                           EXCHANGE_CHECK='exchange', OS_CHECK='os', BACK_ARROW='back',
                           MapDetectionError=MapNameFailure)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = range(5)
        ui.handle_map_event.return_value = False
        ui.appear_then_click.return_value = False
        ui.is_in_globe.return_value = False
        ui.appear.return_value = False
        ui.is_in_map.return_value = True
        ui.get_current_zone.side_effect = MapNameFailure
        ui.get_current_zone_from_globe.return_value = 'observed-zone'
        self.assertEqual(zone_init(ui), 'observed-zone')
        self.assertEqual(ui.get_current_zone.call_count, 2)
        ui.get_current_zone_from_globe.assert_called_once()
        ui.get_current_zone.reset_mock()
        ui.get_current_zone_from_globe.reset_mock()
        zone_init(ui, fallback_init=False)
        self.assertEqual(ui.get_current_zone.call_count, 5)
        ui.get_current_zone_from_globe.assert_not_called()
        for server in ('cn', 'jp', 'en', 'tw'):
            ui.config.SERVER = server
            ui.appear.side_effect = lambda button, **kwargs: button == 'os'
            ui.get_current_zone.reset_mock()
            zone_init(ui)
            self.assertEqual(ui.get_current_zone.call_count, 5, server)


if __name__ == '__main__':
    unittest.main()
