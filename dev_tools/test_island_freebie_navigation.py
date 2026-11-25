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
                 ISLAND_FREEBIE_COOLDOWN='cooldown', ISLAND_FREEBIE_UNAVAILABLE='unavailable',
                 ISLAND_FREEBIE_SHARE='share', STORY_SKIP='story',
                 page_island='island', page_island_phone='phone', page_island_manage='manage')
    exec(compile(tree, 'module/island/freebie.py', 'exec'), scope)
    return scope[name]


class IslandFreebieNavigationTest(unittest.TestCase):
    def test_already_received_supply_does_not_share_or_collect_again(self):
        ui = SimpleNamespace(device=Mock(), appear=lambda b, **kw: b == 'share')
        self.assertTrue(method('freebie_receive')(ui))
        ui.device.click.assert_not_called()

    def test_korean_cooldown_notice_still_checks_uncollected_supply(self):
        ui = SimpleNamespace(ui_ensure=Mock(), island_freebie_notice_appear=lambda: False,
            match_template_color=lambda *args, **kwargs: True,
            freebie_move_to=Mock(), freebie_claim=lambda: True, freebie_receive=lambda: False,
            config=Mock(SERVER='kr'))
        method('run')(ui)
        ui.freebie_move_to.assert_called_once()
        ui.config.task_delay.assert_called_once_with(success=False)

    def test_claim_asset_uses_korean_text(self):
        tree = ast.parse(Path('module/island/assets.py').read_text(encoding='utf-8'))
        for name in ('ISLAND_FREEBIE_CLAIM', 'ISLAND_FREEBIE_COOLDOWN'):
            call = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                        and n.targets[0].id == name)
            files = ast.literal_eval(next(k.value for k in call.keywords if k.arg == 'file'))
            self.assertEqual(files['kr'], './assets/kr/island/{}.png'.format(name))
            self.assertTrue(Path(files['kr']).is_file())

    def test_unknown_scene_does_not_click_story_skip_coordinates(self):
        ui = SimpleNamespace(loop=lambda **kw: iter([1]),
            appear=lambda *args, **kwargs: False, appear_then_click=lambda *args, **kwargs: False,
            ui_page_appear=lambda *args, **kwargs: False, device=Mock(),
            config=SimpleNamespace(SERVER='kr'))
        self.assertFalse(method('freebie_claim')(ui))
        ui.device.click.assert_not_called()
        ui.device.image_save.assert_called_once()

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
