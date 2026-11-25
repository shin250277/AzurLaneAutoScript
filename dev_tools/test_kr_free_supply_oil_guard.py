import unittest
from unittest.mock import Mock, patch

from module.freebies import supply_pack as pack


class FreeSupplyOilGuard(unittest.TestCase):
    def test_timeout_is_not_a_zero_balance(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        with patch.object(pack, 'Timer') as timer:
            timer.return_value.start.return_value.reached.return_value = True
            self.assertIsNone(pack.SupplyPack_250814.get_oil(ui))
        ui.device.click.assert_not_called()

    def test_unreadable_at_cap_and_below_cap(self):
        for oil, expected in [(None, False), (21000, False), (21001, False), (20999, True)]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.config.SupplyPack_DayOfWeek = 0
            ui.get_oil.return_value = oil
            with patch.object(pack, 'get_server_weekday', return_value=0):
                pack.SupplyPack.run(ui)
            self.assertEqual(ui.supply_pack_buy.called, expected)
            if expected:
                ui.supply_pack_buy.assert_called_once_with(pack.FREE_SUPPLY_PACK)
