"""Exercise the production-to-owned-recipe handoff without devices/config writes."""
import ast
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from module.exception import RequestHumanTakeover


class OwnedDispatchTest(unittest.TestCase):
    def make_ui(self, complete):
        tree = ast.parse(Path('module/island/production.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'IslandProduction')
        cls.bases = [ast.Name(id='Base', ctx=ast.Load())]
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'dispatch_slot']
        tree.body = [cls]
        class Base:
            def run(self, slot_id):
                return self.base_run(slot_id=slot_id)
        scope = dict(Base=Base, DIC_ISLAND_PRODUCTION_PLACE={102: {'slot': []}},
                     RequestHumanTakeover=RequestHumanTakeover, del_cached_property=Mock(), logger=Mock(),
                     page_island_manage=SimpleNamespace(check_button='manage'))
        exec(compile(ast.fix_missing_locations(tree), 'production', 'exec'), scope)
        ui = scope['IslandProduction']()
        ui.config = SimpleNamespace(SERVER='kr')
        ui.kr_recipe_audit_complete = complete
        ui.kr_verified_recipe_slots = {9011} if complete else set()
        ui.slot_finish_time = {}
        ui.loop = Mock(side_effect=[iter([None]), iter([None])])
        ui.is_in_island_dock = lambda: True
        ui.is_in_recipe_menu = lambda: True
        ui.island_dock_select_manjuu = Mock()
        ui.island_dock_select_confirm = Mock()
        ui.scan_all_recipe_stocks = Mock(return_value={401001: 10})
        ui.probe_korean_recipe_counters = Mock(return_value={401001: None})
        ui.handle_island_additional = lambda: False
        ui.match_template_color = lambda *a, **kw: True
        ui.base_run = Mock(return_value=datetime(2026, 11, 9, 8))
        return ui

    def test_uncompleted_audit_cannot_reach_owned_runner(self):
        ui = self.make_ui(False)
        with self.assertRaisesRegex(RequestHumanTakeover, 'completed current-run'):
            ui.dispatch_slot(9011, 'slot')
        ui.base_run.assert_not_called()
        self.assertEqual(ui.slot_finish_time, {})

    def test_verified_handoff_records_only_returned_completion(self):
        ui = self.make_ui(True)
        self.assertTrue(ui.dispatch_slot(9011, 'slot'))
        ui.base_run.assert_called_once_with(slot_id=9011)
        self.assertEqual(ui.slot_finish_time, {9011: datetime(2026, 11, 9, 8)})

    def test_audit_exception_cannot_start_or_record_a_slot(self):
        ui = self.make_ui(True)
        ui.probe_korean_recipe_counters.side_effect = RequestHumanTakeover('invalid counters')
        with self.assertRaisesRegex(RequestHumanTakeover, 'invalid counters'):
            ui.dispatch_slot(9011, 'slot')
        ui.base_run.assert_not_called()
        self.assertEqual(ui.slot_finish_time, {})

    def test_completed_audit_does_not_authorize_an_unverified_slot(self):
        ui = self.make_ui(True)
        with self.assertRaisesRegex(RequestHumanTakeover, 'verified recipe group'):
            ui.dispatch_slot(9012, 'other')
        ui.island_dock_select_manjuu.assert_not_called()
        ui.base_run.assert_not_called()

    def test_missing_slot_authority_is_fail_closed(self):
        ui = self.make_ui(True)
        del ui.kr_verified_recipe_slots
        with self.assertRaisesRegex(RequestHumanTakeover, 'verified recipe group'):
            ui.dispatch_slot(9011, 'slot')
        ui.base_run.assert_not_called()
