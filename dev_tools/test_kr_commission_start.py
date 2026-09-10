"""A KR start click is not evidence that a commission started."""
import ast
import copy
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class CommissionStartTest(unittest.TestCase):
    def test_three_identical_commissions_keep_distinct_occurrences(self):
        path = Path('module/commission/commission.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == '_commission_detect')]

        class Occurrence:
            def __init__(self, image, y, config):
                self.repeat_count = 1

            def __eq__(self, other):
                return self.repeat_count == other.repeat_count

        scope = dict(logger=Mock(), lines_detect=lambda image: [200, 350, 500],
                     Commission=Occurrence, SelectedGrids=list)
        exec(compile(tree, str(path), 'exec'), scope)
        result = scope['_commission_detect'](SimpleNamespace(config=Mock()), None)
        self.assertEqual([c.repeat_count for c in result], [1, 2, 3])
        self.assertNotEqual(result[1], result[2])

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
        scope = dict(logger=Mock(), copy=copy, timedelta=timedelta, KR_COMMISSION_OIL_CONFIRM='oil_notice',
                     OCR_KR_COMMISSION_OIL=Mock(ocr=Mock(return_value=10)))
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(handle_info_bar=Mock(), device=Mock(),
                             appear=Mock(return_value=False),
                             handle_popup_confirm=Mock(return_value=True),
                             oil_ocr=scope['OCR_KR_COMMISSION_OIL'],
                             handle_popup_cancel=Mock(return_value=False),
                             _commission_mode_reset=Mock(return_value=mode),
                             _commission_swipe_to_top=Mock(),
                             _commission_scan_list=Mock(return_value=items))
        return scope['_kr_commission_start_confirmed'], ui

    def test_urgent_departure_loses_expiry_and_changes_fallback_category(self):
        from module.commission.project import Commission
        from module.map.map_grids import SelectedGrids
        pending = Commission.__new__(Commission)
        pending.valid = True
        pending.genre = 'urgent_drill'
        pending.category_str, pending.genre_str = 'urgent', 'drill'
        pending.status = 'pending'
        pending.duration = timedelta(minutes=70)
        pending.expire = timedelta(hours=1, minutes=46)
        pending.repeat_count = 1
        running = copy.deepcopy(pending)
        running.genre, running.category_str = 'extra_drill', 'extra'
        running.status = 'running'
        running.duration -= timedelta(seconds=3)
        running.expire = timedelta(0)
        confirm, ui = self.confirm(items=SelectedGrids([running]))
        self.assertTrue(confirm(ui, pending, is_urgent=True))
        self.assertEqual(pending.genre, 'urgent_drill')
        self.assertEqual(pending.expire, timedelta(hours=1, minutes=46))
        running.duration = timedelta(minutes=65)
        self.assertFalse(confirm(ui, pending, is_urgent=True))
        running.duration = timedelta(minutes=70)
        running.status = 'pending'
        self.assertFalse(confirm(ui, pending, is_urgent=True))
        # An eight-hour urgent commission crosses the fallback classification
        # boundary as soon as its countdown begins.
        pending.duration = timedelta(hours=8)
        running.status = 'running'
        running.duration = timedelta(hours=8, seconds=-3)
        running.genre, running.category_str, running.genre_str = 'extra_drill', 'extra', 'drill'
        self.assertTrue(confirm(ui, pending, is_urgent=True))

    def test_ten_oil_notice_can_confirm_but_still_requires_running(self):
        confirm, ui = self.confirm(items=[FakeCommission('pending')])
        ui.appear.return_value = True
        self.assertFalse(confirm(ui, FakeCommission('pending')))
        ui.handle_popup_confirm.assert_called_once_with('COMMISSION_OIL_10')

    def test_limited_daily_departure_also_loses_expiry(self):
        from module.commission.project import Commission
        pending = Commission.__new__(Commission)
        pending.valid = True
        pending.genre = 'urgent_drill'
        pending.category_str, pending.genre_str = 'urgent', 'drill'
        pending.status = 'pending'
        pending.duration = timedelta(hours=4)
        pending.expire = timedelta(hours=1, minutes=53)
        pending.repeat_count = 1
        running = copy.deepcopy(pending)
        running.genre, running.category_str, running.genre_str = 'extra_drill', 'extra', 'drill'
        running.status = 'running'
        running.duration -= timedelta(seconds=6)
        running.expire = timedelta(0)
        confirm, ui = self.confirm(items=[running])
        self.assertTrue(confirm(ui, pending, is_urgent=False))
        self.assertEqual(pending.expire, timedelta(hours=1, minutes=53))
        running.status = 'pending'
        self.assertFalse(confirm(ui, pending, is_urgent=False))

    def test_unknown_popup_is_never_confirmed(self):
        confirm, ui = self.confirm(items=[FakeCommission('pending')])
        self.assertFalse(confirm(ui, FakeCommission('pending')))
        ui.handle_popup_confirm.assert_not_called()

    def test_unverified_oil_amount_is_not_confirmed(self):
        for amount in (0, 100, 1000):
            confirm, ui = self.confirm(items=[FakeCommission('pending')])
            ui.appear.return_value = True
            ui.oil_ocr.ocr.return_value = amount
            self.assertFalse(confirm(ui, FakeCommission('pending')))
            ui.handle_popup_confirm.assert_not_called()

    def test_obscuring_popup_is_not_success(self):
        confirm, ui = self.confirm(mode=False)
        self.assertFalse(confirm(ui, FakeCommission('pending')))
        ui._commission_scan_list.assert_not_called()

    def test_pending_commission_is_not_success(self):
        confirm, ui = self.confirm(items=[FakeCommission('pending')])
        self.assertFalse(confirm(ui, FakeCommission('pending')))
        ui.device.image_save.assert_any_call('./log/kr_commission_departure_pending.png')

    def test_departure_frame_is_saved_before_popup_handling(self):
        confirm, ui = self.confirm(items=[FakeCommission('running')])
        events = []
        ui.device.screenshot.side_effect = lambda: events.append('screenshot')
        ui.device.image_save.side_effect = lambda path: events.append(path)
        ui.handle_info_bar.side_effect = lambda: events.append('info_bar')
        self.assertTrue(confirm(ui, FakeCommission('pending')))
        self.assertEqual(events[:3], [
            'screenshot', './log/kr_commission_departure_before_handling.png', 'info_bar'])

    def test_running_commission_confirms_departure(self):
        confirm, ui = self.confirm(items=[FakeCommission('running')])
        self.assertTrue(confirm(ui, FakeCommission('pending')))

    def test_abandon_popup_is_cancelled_before_list_verification(self):
        confirm, ui = self.confirm(items=[FakeCommission('running')])
        ui.handle_popup_cancel.return_value = True
        self.assertTrue(confirm(ui, FakeCommission('pending')))
        ui.handle_popup_cancel.assert_called_once_with('COMMISSION_DEPARTURE_VERIFY')
        self.assertEqual(ui.device.screenshot.call_count, 3)


class FakeCommission:
    genre = 'extra_drill'
    def __init__(self, status):
        self.status = status

    def convert_to_running(self):
        self.status = 'running'

    def __eq__(self, other):
        return self.status == other.status


if __name__ == '__main__':
    unittest.main()
