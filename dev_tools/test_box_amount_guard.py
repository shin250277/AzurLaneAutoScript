import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class BoxAmountGuardTest(unittest.TestCase):
    def test_confirmation_requires_positive_bounded_amount(self):
        path = Path('module/storage/storage.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'StorageHandler')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_storage_use_one_box')]
        scope = {n.id: n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id.isupper()}
        scope.update(logger=Mock(), RequestHumanTakeover=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        for amount in (0, -1, 16, 1, 15):
            ui = SimpleNamespace(interval_clear=Mock(), interval_reset=Mock(), loop=lambda: range(1),
                                 _storage_in_material=Mock(return_value=False),
                                 appear_then_click=Mock(return_value=False), appear=Mock(return_value=False),
                                 match_template_color=Mock(return_value=True),
                                 _handle_use_box_amount=Mock(return_value=amount), device=Mock())
            if 1 <= amount <= 15:
                scope['_storage_use_one_box'](ui, 'box', amount=15)
                ui.device.click.assert_called_once_with('BOX_AMOUNT_CONFIRM')
            else:
                with self.assertRaises(RuntimeError):
                    scope['_storage_use_one_box'](ui, 'box', amount=15)
                ui.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
