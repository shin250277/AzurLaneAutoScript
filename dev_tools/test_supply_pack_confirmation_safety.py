"""Never confirm a purchase that the supply-pack task did not select."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class Takeover(Exception):
    pass


def load_buy():
    path = 'module/freebies/supply_pack.py'
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == 'supply_pack_buy')]
    timer = Mock()
    timer.return_value.start.return_value.reached.return_value = True
    scope = dict(logger=Mock(), Timer=timer, HumanTakeover=Takeover,
                 GET_ITEMS_1='items1', GET_ITEMS_2='items2', BUY_CONFIRM='buy',
                 page_supply_pack=SimpleNamespace(check_button='page'))
    exec(compile(tree, path, 'exec'), scope)
    return scope['supply_pack_buy']


class SupplyPackConfirmationSafetyTest(unittest.TestCase):
    def harness(self):
        return SimpleNamespace(
            device=Mock(), interval_clear=Mock(), interval_reset=Mock(),
            appear=Mock(return_value=False), appear_then_click=Mock(return_value=False),
            handle_popup_confirm=Mock(return_value=False))

    def test_unknown_purchase_confirmation_stops_without_confirming(self):
        ui = self.harness()
        ui.appear.side_effect = lambda button, **kw: button in ('buy', 'page')
        with self.assertRaises(Takeover):
            load_buy()(ui, 'free')
        ui.device.click.assert_not_called()
        ui.handle_popup_confirm.assert_not_called()
        ui.appear_then_click.assert_not_called()

    def test_no_selection_never_calls_purchase_confirmation_handlers(self):
        ui = self.harness()
        ui.appear.side_effect = lambda button, **kw: button == 'page'
        self.assertFalse(load_buy()(ui, 'free'))
        ui.handle_popup_confirm.assert_not_called()
        self.assertNotIn('buy', [c[0][0] for c in ui.appear_then_click.call_args_list])

    def test_selected_pack_can_complete_confirmation(self):
        ui = self.harness()
        frame = [0]
        def screenshot():
            frame[0] += 1
            self.assertLess(frame[0], 4, 'purchase did not finish')
        ui.device.screenshot.side_effect = screenshot
        ui.appear.side_effect = lambda button, **kw: (
            button == 'page' or (button == 'free' and frame[0] == 0))
        ui.handle_popup_confirm.side_effect = lambda *a: frame[0] == 1
        self.assertTrue(load_buy()(ui, 'free'))
        ui.device.click.assert_called_once_with('free')
        ui.interval_reset.assert_any_call('free')


if __name__ == '__main__':
    unittest.main()
