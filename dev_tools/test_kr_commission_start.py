"""A KR start click is not evidence that a commission started."""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class CommissionStartTest(unittest.TestCase):
    def test_start_click_waits_for_confirmation(self):
        path = Path(__file__).resolve().parents[1] / 'module/commission/commission.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == '_commission_start_click')
        tree.body = [method]
        scope = dict(logger=Mock(), Timer=Mock(return_value=Mock()),
                     COMMISSION_ADVICE='advice', COMMISSION_START='start')
        exec(compile(tree, str(path), 'exec'), scope)
        handler = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  interval_clear=Mock(), interval_reset=Mock(),
                                  info_bar_count=Mock(side_effect=[0, 1]),
                                  _kr_commission_start_confirmed=Mock(return_value=True),
                                  appear=Mock(return_value=True), device=Mock())
        self.assertTrue(scope['_commission_start_click'](handler, Mock()))
        handler.device.click.assert_called_once_with('start')
        self.assertEqual(handler.info_bar_count.call_count, 1)
        handler.device.sleep.assert_called_once_with(1)
        handler._kr_commission_start_confirmed.assert_called_once()

    def confirm(self, mode=True, items=()):
        path = Path('module/commission/commission.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_commission_start_confirmed')]
        scope = dict(logger=Mock(), copy=copy)
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(handle_info_bar=Mock(), device=Mock(),
                             handle_popup_cancel=Mock(return_value=False),
                             _commission_mode_reset=Mock(return_value=mode),
                             _commission_swipe_to_top=Mock(),
                             _commission_scan_list=Mock(return_value=items))
        return scope['_kr_commission_start_confirmed'], ui

    def test_obscuring_popup_is_not_success(self):
        confirm, ui = self.confirm(mode=False)
        self.assertFalse(confirm(ui, FakeCommission('pending')))
        ui._commission_scan_list.assert_not_called()

    def test_pending_commission_is_not_success(self):
        confirm, ui = self.confirm(items=[FakeCommission('pending')])
        self.assertFalse(confirm(ui, FakeCommission('pending')))

    def test_running_commission_confirms_departure(self):
        confirm, ui = self.confirm(items=[FakeCommission('running')])
        self.assertTrue(confirm(ui, FakeCommission('pending')))

    def test_abandon_popup_is_cancelled_before_list_verification(self):
        confirm, ui = self.confirm(items=[FakeCommission('running')])
        ui.handle_popup_cancel.return_value = True
        self.assertTrue(confirm(ui, FakeCommission('pending')))
        ui.handle_popup_cancel.assert_called_once_with('COMMISSION_DEPARTURE_VERIFY')
        self.assertEqual(ui.device.screenshot.call_count, 2)


class FakeCommission:
    def __init__(self, status):
        self.status = status

    def convert_to_running(self):
        self.status = 'running'

    def __eq__(self, other):
        return self.status == other.status


if __name__ == '__main__':
    unittest.main()
