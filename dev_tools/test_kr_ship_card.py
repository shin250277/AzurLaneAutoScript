"""KR ship cards can be dismissed independently of EXP ordering."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class ShipCardTest(unittest.TestCase):
    def test_contextual_card_click_stays_outside_dialogue(self):
        for path, name in [('module/combat/combat.py', 'KR_SHIP_CARD'),
                           ('module/ui/ui.py', 'KR_UI_SHIP_CARD')]:
            with self.subTest(handler=name):
                tree = ast.parse(Path(path).read_text(encoding='utf-8'))
                value = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                             and any(isinstance(t, ast.Name) and t.id == name
                                     for t in n.targets))
                target = ast.literal_eval(next(k.value for k in value.keywords
                                               if k.arg == 'button'))
                self.assertEqual(target, (980, 650, 1030, 680))

    def setUp(self):
        path = Path('module/combat/combat.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Combat')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'handle_kr_ship_card')]
        scope = {'KR_SHIP_CARD': 'card', 'NEW_SHIP': 'new'}
        exec(compile(tree, str(path), 'exec'), scope)
        self.handle = scope['handle_kr_ship_card']
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr', GET_SHIP_TRIGGERED=False),
                                  appear=Mock(side_effect=[True, False]), device=Mock())

    def test_existing_card_is_not_marked_new(self):
        self.assertTrue(self.handle(self.ui))
        self.ui.device.click.assert_called_once_with('card')
        self.assertFalse(self.ui.config.GET_SHIP_TRIGGERED)

    def test_new_card_sets_trigger_and_records_drop(self):
        self.ui.appear.side_effect = [True, True]
        drop = Mock()
        self.assertTrue(self.handle(self.ui, drop=drop))
        self.assertTrue(self.ui.config.GET_SHIP_TRIGGERED)
        drop.handle_add.assert_called_once_with(self.ui)
        self.ui.device.click.assert_called_once_with('card')

    def test_new_card_without_recorder_still_sets_trigger(self):
        self.ui.appear.side_effect = [True, True]
        self.assertTrue(self.handle(self.ui))
        self.assertTrue(self.ui.config.GET_SHIP_TRIGGERED)
        self.ui.device.click.assert_called_once_with('card')

    def test_other_server_does_not_click(self):
        self.ui.config.SERVER = 'jp'
        self.assertFalse(self.handle(self.ui))
        self.ui.device.click.assert_not_called()

    def test_missing_card_does_not_click(self):
        self.ui.appear.side_effect = [False]
        self.assertFalse(self.handle(self.ui))
        self.ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
