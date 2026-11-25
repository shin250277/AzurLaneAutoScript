import unittest
from unittest.mock import Mock
from module.island_handler.kr_coin_material import find_stable_shop_item


class MaterialShopStabilityTest(unittest.TestCase):
    def test_transient_unknown_requires_two_matching_fresh_positions(self):
        ui = Mock()
        ui.island_shop_get_item_ids.side_effect = [[None], [None, 411004], [None, 411004]]
        self.assertEqual(find_stable_shop_item(ui, 411004), 1)
        self.assertEqual(ui.device.screenshot.call_count, 3)
        ui.device.click.assert_not_called()

    def test_changed_position_is_not_accepted_until_stable(self):
        ui = Mock()
        ui.island_shop_get_item_ids.side_effect = [[411004], [None, 411004], [411004], [None]]
        self.assertIsNone(find_stable_shop_item(ui, 411004))
        ui.device.click.assert_not_called()

    def test_duplicate_and_missing_targets_are_never_guessed(self):
        for ids in ([411004, 411004], [None, 411000], []):
            ui = Mock()
            ui.island_shop_get_item_ids.return_value = ids
            self.assertIsNone(find_stable_shop_item(ui, 411004))
            self.assertEqual(ui.island_shop_get_item_ids.call_count, 4)
            ui.device.click.assert_not_called()
