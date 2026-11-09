import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class ProductionCharacterTest(unittest.TestCase):
    def test_kr_requires_modal_and_localized_text(self):
        tree = ast.parse(Path('module/island/production.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'handle_production_character_entry')]
        scope = dict(KR_PRODUCTION_SELECT_CHARACTER='kr', ISLAND_PRODUCTION_SELECT_CHARACTER='foreign')
        exec(compile(tree, 'production', 'exec'), scope)
        for modal, matched, expected in ((False, True, False), (True, False, False), (True, True, True)):
            ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                 is_enter_window_shown=lambda: modal,
                                 appear_then_click=Mock(return_value=matched))
            self.assertEqual(scope['handle_production_character_entry'](ui), expected)
            if modal:
                ui.appear_then_click.assert_called_once_with('kr', offset=(20, 20), interval=1)
            else:
                ui.appear_then_click.assert_not_called()
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='jp'),
                             appear_then_click=Mock(return_value=True))
        self.assertTrue(scope['handle_production_character_entry'](ui))
        ui.appear_then_click.assert_called_once_with('foreign', offset=(60, 20), interval=1)

    def test_entry_timeout_stops_before_worker_or_recipe_selection(self):
        from module.exception import RequestHumanTakeover
        tree = ast.parse(Path('module/island/production.py').read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'dispatch_slot')]
        scope = dict(DIC_ISLAND_PRODUCTION_PLACE={102: {'slot': []}},
                     RequestHumanTakeover=RequestHumanTakeover,
                     page_island_manage=SimpleNamespace(check_button='manage'))
        exec(compile(tree, 'production', 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             kr_recipe_audit_complete=True, kr_verified_recipe_slots={9111},
                             loop=Mock(return_value=iter([None, None])),
                             is_in_island_dock=lambda: False,
                             handle_production_character_entry=lambda: False,
                             match_template_color=lambda *a, **kw: False,
                             device=Mock())
        with self.assertRaisesRegex(RequestHumanTakeover, 'entry not confirmed'):
            scope['dispatch_slot'](ui, 9111, 'slot')
        ui.loop.assert_called_once_with(timeout=15)
        ui.device.click.assert_not_called()

    def test_text_asset_matches_but_blank_does_not(self):
        import numpy as np
        from module.base.button import Button
        from module.base.utils import load_image
        tree = ast.parse(Path('module/island/production.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'KR_PRODUCTION_SELECT_CHARACTER' for t in n.targets))
        button = Button(**{k.arg: ast.literal_eval(k.value) for k in node.value.keywords})
        public = load_image(button.file)
        self.assertTrue(button.match(public, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(public), offset=(20, 20)))
