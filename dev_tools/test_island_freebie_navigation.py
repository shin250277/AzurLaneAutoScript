"""Wait for the freebie scene and never mark a failed collection successful."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def method(name):
    tree = ast.parse(Path('module/island/freebie.py').read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)]
    scope = dict(logger=Mock(), Timer=Mock(), ISLAND_FREEBIE_CLAIM='claim',
                 ISLAND_FREEBIE_COOLDOWN='cooldown', STORY_SKIP='story',
                 page_island='island', page_island_phone='phone', page_island_manage='manage')
    exec(compile(tree, 'module/island/freebie.py', 'exec'), scope)
    return scope[name]


class IslandFreebieNavigationTest(unittest.TestCase):
    def test_claim_waits_for_scene_instead_of_rejecting_first_frame(self):
        ui = SimpleNamespace(loop=lambda **kw: iter([1, 2]),
            appear=lambda button, **kw: button == 'cooldown',
            appear_then_click=Mock(side_effect=[True, False]), device=Mock())
        self.assertTrue(method('freebie_claim')(ui))
        self.assertEqual(ui.appear_then_click.call_count, 2)

    def test_failed_claim_or_receive_defers_without_sharing(self):
        for claimed, received in ((False, False), (True, False)):
            with self.subTest(claimed=claimed):
                ui = SimpleNamespace(ui_ensure=Mock(), island_freebie_notice_appear=lambda: True,
                    freebie_move_to=Mock(), freebie_claim=Mock(return_value=claimed),
                    freebie_receive=Mock(return_value=received), freebie_share=Mock(), config=Mock())
                method('run')(ui)
                ui.config.task_delay.assert_called_once_with(success=False)
                ui.freebie_share.assert_not_called()
                if not claimed:
                    ui.freebie_receive.assert_not_called()

    def test_successful_collection_with_share_disabled_does_not_share(self):
        ui = SimpleNamespace(ui_ensure=Mock(), island_freebie_notice_appear=lambda: True,
            freebie_move_to=Mock(), freebie_claim=lambda: True, freebie_receive=lambda: True,
            freebie_share=Mock(), config=Mock(IslandFreebie_Share=False))
        method('run')(ui)
        ui.config.task_delay.assert_called_once_with(server_update=True)
        ui.freebie_share.assert_not_called()


if __name__ == '__main__':
    unittest.main()
