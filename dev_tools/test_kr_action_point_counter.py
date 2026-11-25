"""Device-free purchase counter safety checks."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class CounterTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/os_handler/action_point.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ActionPointHandler')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                      and n.name == 'action_point_get_buy_remain')
        tree.body = [method]
        self.ocr = Mock()
        scope = dict(OCR_ACTION_POINT_BUY_REMAIN=self.ocr, logger=Mock(), RequestHumanTakeover=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        self.read = scope['action_point_get_buy_remain']
        self.handler = SimpleNamespace(loop=lambda timeout: range(3), device=SimpleNamespace(image=None))

    def test_valid_remaining(self):
        for current in range(6):
            self.ocr.ocr.return_value = (current, 5-current, 5)
            self.assertEqual(self.read(self.handler), current)

    def test_invalid_counter_stops(self):
        for result in [(0, 0, 0), (5, 0, 0), (6, -1, 5), (-1, 6, 5), (4, 0, 4)]:
            self.ocr.ocr.return_value = result
            with self.assertRaises(RuntimeError):
                self.read(self.handler)

    def test_transient_invalid_counter_retries(self):
        self.ocr.ocr.side_effect = [(0, 0, 0), (5, 0, 5)]
        self.assertEqual(self.read(self.handler), 5)


class PurchaseSelectionTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/os_handler/action_point.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ActionPointHandler')
        tree.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'action_point_buy']
        scope = dict(ACTION_POINTS_BUY={5: 1000}, logger=Mock(), RequestHumanTakeover=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        self.buy = scope['action_point_buy']
        self.handler = Mock()
        self.handler.config = SimpleNamespace(SERVER='kr', OpsiGeneral_BuyActionPointLimit=1)
        self.handler._action_point_box = {0: 10000}
        self.handler.action_point_get_buy_remain.return_value = 5
        self.handler.action_point_set_button.return_value = True

    def test_failed_oil_selection_never_uses_current_item(self):
        self.handler.action_point_set_button.return_value = False
        with self.assertRaises(RuntimeError):
            self.buy(self.handler)
        self.handler.action_point_use.assert_not_called()
        self.handler.action_point_get_buy_remain.assert_not_called()

    def test_verified_oil_selection_keeps_authorized_purchase_path(self):
        self.assertTrue(self.buy(self.handler))
        self.handler.action_point_set_button.assert_called_once_with(0)
        self.handler.action_point_use.assert_called_once_with()

    def test_purchase_cap_still_blocks_use(self):
        self.handler.action_point_get_buy_remain.return_value = 4
        self.assertFalse(self.buy(self.handler))
        self.handler.action_point_use.assert_not_called()


class BoxSelectionTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/os_handler/action_point.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ActionPointHandler')
        tree.body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                     and n.name in ('handle_action_point', 'action_point_get_active_button')]
        self.color = Mock(return_value=(100, 100, 100))
        grid = SimpleNamespace(buttons=[SimpleNamespace(area=(0, 0, 10, 10)) for _ in range(4)])
        scope = dict(ACTION_POINT_BOX={1: 20, 2: 50, 3: 100}, ACTION_POINT_GRID=grid,
                     get_color=self.color, logger=Mock(), RequestHumanTakeover=RuntimeError,
                     ActionPointLimit=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        self.handle, self.active = scope['handle_action_point'], scope['action_point_get_active_button']
        self.ui = Mock()
        self.ui.config = SimpleNamespace(SERVER='kr', OpsiGeneral_BuyActionPointLimit=0,
                                         OS_ACTION_POINT_PRESERVE=0)
        self.ui._action_point_current, self.ui._action_point_total = 0, 20
        self.ui._action_point_box = {1: 1, 2: 0, 3: 0}
        self.ui.action_point_set_button.return_value = True
        self.ui.action_point_use.side_effect = lambda: setattr(self.ui, '_action_point_current', 20)

    def test_failed_box_selection_never_consumes_item(self):
        self.ui.action_point_set_button.return_value = False
        with self.assertRaises(RuntimeError):
            self.handle(self.ui, None, None, cost=20)
        self.ui.action_point_use.assert_not_called()

    def test_confirmed_box_selection_and_updated_ap_succeed(self):
        self.assertTrue(self.handle(self.ui, None, None, cost=20))
        self.ui.action_point_set_button.assert_called_once_with(1)
        self.ui.action_point_use.assert_called_once_with()

    def test_unknown_active_button_is_not_assumed_to_be_box_one(self):
        self.assertEqual(self.active(self.ui), -1)

    def test_other_server_keeps_existing_unknown_button_fallback(self):
        self.ui.config.SERVER = 'jp'
        self.assertEqual(self.active(self.ui), 1)

    def test_visible_active_button_is_still_detected(self):
        self.color.side_effect = [(100, 100, 100), (100, 100, 200)]
        self.assertEqual(self.active(self.ui), 1)


class PopupRecoveryTest(unittest.TestCase):
    def test_cancel_only_after_ap_checks(self):
        path = Path(__file__).resolve().parents[1] / 'module/ui/ui.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'UI')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'ui_page_os_popups')
        tree.body = [method]
        scope = dict(server=SimpleNamespace(server='kr'), logger=Mock(), RequestHumanTakeover=RuntimeError)
        for name in ['CURRENT_AP_CHECK', 'ACTION_POINT_USE', 'ACTION_POINT_CANCEL',
                     'RESET_TICKET_POPUP', 'RESET_FLEET_PREPARATION', 'EXCHANGE_CHECK']:
            scope[name] = name
        exec(compile(tree, str(path), 'exec'), scope)
        for current_ap, use, expected in [(True, True, True), (False, True, False), (True, False, False)]:
            handler = SimpleNamespace(
                _opsi_reset_fleet_preparation_click=0,
                match_template_color=Mock(return_value=current_ap),
                appear=Mock(side_effect=lambda button, **kw: use if button == 'ACTION_POINT_USE' else False),
                appear_then_click=Mock(side_effect=lambda button, **kw: button == 'ACTION_POINT_CANCEL'))
            self.assertEqual(scope['ui_page_os_popups'](handler), expected)
            clicked = [call[0][0] for call in handler.appear_then_click.call_args_list]
            self.assertEqual('ACTION_POINT_CANCEL' in clicked, expected)
            self.assertNotIn('ACTION_POINT_USE', clicked)


if __name__ == '__main__':
    unittest.main()
