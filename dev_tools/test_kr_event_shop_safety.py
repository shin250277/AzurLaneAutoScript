"""KR event-shop scans must not implicitly treat every price as event points."""
import unittest
import subprocess
import sys
from unittest.mock import Mock
from types import SimpleNamespace
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped
from module.shop_event.korean_currency import validated_point_items


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
        run = method('module/shop_event/shop_event.py', 'EventShop', '_run', FILTER=filters,
                     KoreanEventCurrency=Mock(), crop=Mock(), validated_point_items=validated_point_items)
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

    def test_verified_points_reach_existing_filter_without_spending_in_test(self):
        filters = Mock()
        filters.apply.return_value = []
        reader = Mock()
        reader.return_value.identify.return_value = 'train_pt'
        run = method('module/shop_event/shop_event.py', 'EventShop', '_run', FILTER=filters,
                     KoreanEventCurrency=reader, crop=Mock(), validated_point_items=validated_point_items)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.EventShop_PresetFilter = 'custom'
        ui.event_shop_has_urpt = False
        item = SimpleNamespace(kr_currency_token='train_pt', cost='pt', price=200,
                               amount=1, count=1, total_count=1)
        ui.scan_all.return_value = [item]
        ui.handle_items_related_with_urpt.return_value = ([item], [])
        ui.handle_unobtained_items.return_value = ([item], [])
        self.assertTrue(run(ui))
        filters.apply.assert_called_once_with([item])
        ui.event_shop_buy_item.assert_not_called()


if __name__ == '__main__':
    unittest.main()
