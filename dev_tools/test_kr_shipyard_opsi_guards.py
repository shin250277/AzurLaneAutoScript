"""Exercise the real KR profile guard paths with synthetic balances, never a device."""
import unittest
from unittest.mock import Mock

from module.os.map import OSMap
from module.os.tasks.daily import OpsiDaily
from module.os_handler.action_point import ActionPointHandler
from module.shipyard.shipyard_reward import RewardShipyard
from module.shipyard.ui import ShipyardUI


class ShipyardAndOpsiGuards(unittest.TestCase):
    def test_unselected_target_cannot_activate_a_ship(self):
        ui = Mock()
        self.assertFalse(ShipyardUI.shipyard_bottom_navbar_ensure(ui, left=0))
        ui._shipyard_bottom_navbar.set.assert_not_called()

    def test_free_and_discount_boundary_for_each_rarity(self):
        for rarity, price in [('PR', 150), ('DR', 600)]:
            for balance, affordable in [(0, 2), (price-1, 2), (price, 3)]:
                ui = Mock(_shipyard_bp_rarity=rarity, _coin_count=balance)
                ui._shipyard_get_cost.side_effect = lambda i: RewardShipyard._shipyard_get_cost(ui, i)
                for pay in (False, True):
                    self.assertEqual(RewardShipyard._shipyard_calculate(ui, 1, 3, pay=pay),
                                     (affordable+1, affordable))
                    self.assertEqual(ui._coin_count, balance - (price if pay and affordable == 3 else 0))

    def test_oil_floor_and_weekly_purchase_cap(self):
        for oil, remaining, expected in [(1999, 5, False), (2000, 5, True), (9000, 4, False)]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.config.OpsiGeneral_BuyActionPointLimit = 1
            ui._action_point_box = [oil]
            ui.action_point_set_button.return_value = True
            ui.action_point_get_buy_remain.return_value = remaining
            self.assertEqual(ActionPointHandler.action_point_buy(ui, preserve=1000), expected)
            self.assertEqual(ui.action_point_use.call_count, int(expected))

    def test_repair_threshold_checks_only_occupied_positions(self):
        for hp, expected in [(.41, False), (.40, True), (.39, True)]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.config.OpsiGeneral_RepairThreshold = .4
            ui.hp_has_ship, ui.hp = [True, False], [hp, 0.]
            ui.is_in_special_zone.return_value = False
            self.assertEqual(OSMap.handle_fleet_repair(ui), expected)
            self.assertEqual(ui.fleet_repair.call_count, int(expected))

    def test_daily_uses_selected_fleet_without_submarine(self):
        ui = Mock()
        ui.config.OpsiFleet_Fleet = 1
        ui.config.OpsiFleet_Submarine = False
        ui.os_get_next_mission.side_effect = ['already_at_mission_zone', False]
        OpsiDaily.os_finish_daily_mission(ui)
        ui.fleet_set.assert_called_once_with(1)
        ui.os_order_execute.assert_called_once_with(recon_scan=False, submarine_call=False)
