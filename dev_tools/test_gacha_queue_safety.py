"""Device-free regression checks for construction queue and shop safety."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class GachaQueueSafetyTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/gacha/gacha_reward.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == 'RewardGacha')
        tree.body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                     and n.name in ('gacha_flush_queue', 'gacha_guard_shop')]
        scope = {n.id: n.id for n in ast.walk(tree)
                 if isinstance(n, ast.Name) and n.id.isupper()}
        self.skip = Mock()
        scope.update(Timer=Mock(), STORY_SKIP=self.skip, page_shop='shop', page_build='build',
                     RequestHumanTakeover=RuntimeError, logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        self.flush = scope['gacha_flush_queue']
        self.guard = scope['gacha_guard_shop']
        self.ui = Mock()
        self.ui.config = SimpleNamespace(SERVER='kr')
        self.ui.appear.return_value = False
        self.ui.appear_then_click.return_value = False
        self.ui.handle_retirement.return_value = False
        self.ui.handle_popup_confirm.return_value = False
        self.ui.handle_get_items_ship.return_value = False

    def test_shop_redirect_stops_without_input(self):
        self.ui.ui_page_appear.return_value = True
        with self.assertRaises(RuntimeError):
            self.guard(self.ui)
        self.ui.device.click.assert_not_called()

    def test_non_shop_continues_without_input(self):
        self.ui.ui_page_appear.return_value = False
        self.guard(self.ui)
        self.ui.device.click.assert_not_called()

    def test_empty_queue_after_receipt_returns_without_finish_click(self):
        empty_checks = iter([False, True])
        def appear(button, **kwargs):
            if button == 'BUILD_QUEUE_EMPTY':
                return next(empty_checks)
            return button == 'GET_SHIP'
        self.ui.appear.side_effect = appear
        self.flush(self.ui)
        self.ui.device.click.assert_called_once_with('GET_SHIP')
        self.ui.gacha_side_navbar_ensure.assert_any_call(upper=1)
        self.ui.gacha_guard_shop.assert_called()

    def test_shop_guard_precedes_finish_and_popup_processing(self):
        self.ui.gacha_guard_shop.side_effect = RuntimeError('shop')
        with self.assertRaises(RuntimeError):
            self.flush(self.ui)
        self.ui.appear_then_click.assert_not_called()
        self.ui.handle_popup_confirm.assert_not_called()
        self.ui.device.click.assert_not_called()

    def test_empty_template_without_build_header_does_not_leave_queue(self):
        self.ui.ui_page_appear.return_value = False
        self.ui.appear.side_effect = lambda button, **kwargs: button == 'BUILD_QUEUE_EMPTY'
        self.ui.gacha_guard_shop.side_effect = [None, RuntimeError('end observation')]
        with self.assertRaises(RuntimeError):
            self.flush(self.ui)
        self.ui.gacha_side_navbar_ensure.assert_called_once_with(bottom=3)

    def test_acquisition_is_handled_before_empty_queue(self):
        self.ui.appear.return_value = True
        self.ui.gacha_guard_shop.side_effect = [None, RuntimeError('end observation')]
        with self.assertRaises(RuntimeError):
            self.flush(self.ui)
        self.ui.device.click.assert_called_once_with('KR_GACHA_NEW_SHIP')
        self.ui.gacha_side_navbar_ensure.assert_called_once_with(bottom=3)


if __name__ == '__main__':
    unittest.main()
