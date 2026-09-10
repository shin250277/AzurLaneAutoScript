"""Repeated item-info screens must not restart KR item consumption forever."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class KoreanStorageItemSafetyTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/os_handler/storage.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                   and node.name == 'StorageHandler')
        tree.body = [next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                         and node.name == '_storage_item_use')]
        scope = {node.id: node.id for node in ast.walk(tree)
                 if isinstance(node, ast.Name) and node.id.isupper()}
        scope.update(logger=Mock(), RequestHumanTakeover=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        self.use = scope['_storage_item_use']
        self.ui = Mock()
        self.ui.config = SimpleNamespace(SERVER='kr')
        self.ui.loop.side_effect = lambda: iter(range(5))
        self.ui.appear.side_effect = lambda button, **kwargs: button == 'GET_MISSION'

    def test_repeated_info_stops_before_outer_item_retry(self):
        with self.assertRaises(RuntimeError):
            self.use(self.ui, 'logger_item')
        self.assertEqual(self.ui.device.click.call_count, 3)
        self.assertTrue(all(call[0] == ('GET_MISSION',) for call in self.ui.device.click.call_args_list))
        self.ui.device.image_save.assert_called_once_with('./log/kr_storage_item_unconfirmed.png')
        self.ui.appear_then_click.assert_not_called()

    def test_other_server_keeps_existing_redetection_behavior(self):
        self.ui.config.SERVER = 'jp'
        self.use(self.ui, 'logger_item')
        self.assertEqual(self.ui.device.click.call_count, 3)
        self.ui.device.image_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
