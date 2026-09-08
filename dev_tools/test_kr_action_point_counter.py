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
