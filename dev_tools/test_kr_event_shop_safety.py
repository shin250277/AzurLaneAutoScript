"""KR event-shop scans must not implicitly treat every price as event points."""
import unittest
import subprocess
import sys
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class KoreanEventShopSafetyTest(unittest.TestCase):
    def test_event_tab_uses_korean_asset(self):
        code = """
import numpy as np
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.shop.assets import NAV_EVENT
assert '/kr/' in NAV_EVENT.file.replace('\\\\', '/')
frame = np.array(Image.open(NAV_EVENT.file).convert('RGB'))
assert NAV_EVENT.match(frame)
assert not NAV_EVENT.match(np.zeros((720, 1280, 3), dtype=np.uint8))
"""
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_unverified_currency_stops_before_buying_or_unlocking(self):
        filters = Mock()
        filters.apply.return_value = []
        run = method('module/shop_event/shop_event.py', 'EventShop', '_run', FILTER=filters)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.EventShop_PresetFilter = 'custom'
        ui.scan_all.return_value = ['observed-item']
        ui.handle_items_related_with_urpt.return_value = ([], [])
        ui.handle_unobtained_items.return_value = ([], [])
        with self.assertRaises(TaskStopped):
            run(ui)
        ui.handle_items_related_with_urpt.assert_not_called()
        ui.handle_unobtained_items.assert_not_called()
        ui.event_shop_buy_item.assert_not_called()
        ui.device.image_save.assert_called_once()


if __name__ == '__main__':
    unittest.main()
