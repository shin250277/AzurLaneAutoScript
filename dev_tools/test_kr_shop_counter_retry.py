"""A second digit model can repair an invalid KR counter, not override valid stock."""
import unittest
from unittest.mock import Mock, patch


class CounterRetryTest(unittest.TestCase):
    def run_prediction(self, original, first, second, region='kr'):
        import module.config.server as server
        from module.shop_event.item import EventShopItemGrid
        from module.statistics.item import ItemGrid
        item = Mock()
        item.name, item.is_ship = 'Oil', False
        grid = EventShopItemGrid.__new__(EventShopItemGrid)
        grid.items, grid.kr_names, grid.kr_currency = [item], None, None
        grid.counter_area = (0, 0, 1, 1)
        grid.counter_ocr = Mock()
        grid.counter_ocr.ocr.return_value = [original]
        reader1, reader2 = Mock(), Mock()
        reader1.ocr.return_value, reader2.ocr.return_value = [first], [second]
        with patch.object(server, 'server', region), patch.object(ItemGrid, 'predict'), \
                patch('module.shop_event.item.CounterOcr', side_effect=[reader1, reader2]) as factory:
            grid.predict(None, amount=False, save_unknown=False)
        return (item.count, item.total_count), factory.call_count

    def test_two_valid_reads_must_agree(self):
        self.assertEqual(self.run_prediction([0,0], [100,100], [100,100]), ((100,100), 2))
        for first, second in (([100,100], [10,100]), ([0,0], [0,0]), ([0,0], [1,1])):
            self.assertEqual(self.run_prediction([0,0], first, second), ((0,0), 2))

    def test_valid_zero_stock_is_not_replaced(self):
        self.assertEqual(self.run_prediction([0,5], [5,5], [5,5]), ((0,5), 0))

    def test_foreign_server_keeps_original_path(self):
        self.assertEqual(self.run_prediction([0,0], [100,100], [100,100], 'jp'), ((0,0), 0))


if __name__ == '__main__':
    unittest.main()
