"""Offline blueprint quantity adjustment boundaries; no shipyard UI is driven."""
import unittest
from unittest.mock import Mock

from dev_tools.test_os_task_stop_boundaries import method


class ShipyardQuantityTest(unittest.TestCase):
    def setUp(self):
        self.ui = Mock()
        self.ensure = method('module/shipyard/ui.py', 'ShipyardUI', '_shipyard_ensure_index')

    def readings(self, values):
        self.ui._shipyard_get_total.side_effect = [('plus', 'minus', value) for value in values]

    def test_decrease_uses_positive_click_count(self):
        self.readings([5, 2])
        self.assertEqual(self.ensure(self.ui, 2), 0)
        self.ui.device.multi_click.assert_called_once_with('minus', n=3, interval=(0.3, 0.5))

    def test_unresolved_excess_quantity_cannot_be_confirmed(self):
        self.readings([5, 5, 5, 5])
        self.assertIsNone(self.ensure(self.ui, 2))

    def test_final_click_is_followed_by_verified_read(self):
        self.readings([0, 0, 0, 2])
        self.assertEqual(self.ensure(self.ui, 2), 0)
        self.assertEqual(self.ui.device.multi_click.call_count, 3)

    def test_partial_available_quantity_returns_nonnegative_remainder(self):
        self.readings([0, 1, 1, 1])
        self.assertEqual(self.ensure(self.ui, 3), 2)

    def test_invalid_ocr_quantity_does_not_click(self):
        self.readings([-1, -1, -1, -1])
        self.assertIsNone(self.ensure(self.ui, 2))
        self.ui.device.multi_click.assert_not_called()

    def test_zero_selected_quantity_does_not_allow_confirmation(self):
        self.readings([0, 0, 0, 0])
        self.assertIsNone(self.ensure(self.ui, 2))

    def test_buy_and_use_do_not_confirm_unresolved_excess(self):
        for name, argument in (('_shipyard_buy', 2), ('_shipyard_use', 1)):
            with self.subTest(operation=name):
                ui = Mock()
                ui._shipyard_buy_calc.return_value = (3, 2)
                ui._shipyard_get_bp_count.return_value = 2
                ui._shipyard_buy_enter.return_value = True
                ui._shipyard_cannot_strengthen.return_value = False
                ui._shipyard_get_total.return_value = ('plus', 'minus', 5)
                ui._shipyard_ensure_index.side_effect = lambda count: self.ensure(ui, count)
                run = method('module/shipyard/shipyard_reward.py', 'RewardShipyard', name)
                run(ui, argument)
                ui._shipyard_buy_confirm.assert_not_called()
                ui._shipyard_pay_calc.assert_not_called()

    def test_buy_and_use_do_not_confirm_empty_selection(self):
        for name, argument in (('_shipyard_buy', 2), ('_shipyard_use', 1)):
            with self.subTest(operation=name):
                ui = Mock()
                ui._shipyard_buy_calc.return_value = (3, 2)
                ui._shipyard_get_bp_count.return_value = 2
                ui._shipyard_buy_enter.return_value = True
                ui._shipyard_cannot_strengthen.return_value = False
                ui._shipyard_get_total.return_value = ('plus', 'minus', 0)
                ui._shipyard_ensure_index.side_effect = lambda count: self.ensure(ui, count)
                run = method('module/shipyard/shipyard_reward.py', 'RewardShipyard', name)
                run(ui, argument)
                ui._shipyard_buy_confirm.assert_not_called()
                ui._shipyard_pay_calc.assert_not_called()


if __name__ == '__main__':
    unittest.main()
