"""UR warnings must stop confirmation before any click."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import numpy as np
from PIL import Image
from module.base.button import Button


class UrSafetyTest(unittest.TestCase):
    def test_guard_raises_before_click(self):
        path = Path(__file__).resolve().parents[1] / 'module/retire/retirement.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Retirement')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_retirement_confirm')
        loop = next(n for n in method.body if isinstance(n, ast.While))
        guard = next(n for n in loop.body if isinstance(n, ast.If)
                     and any(isinstance(x, ast.Name) and x.id == 'KR_RETIRE_UR_WARNING'
                             for x in ast.walk(n.test)))
        first_click = next(i for i, n in enumerate(loop.body)
                           if any(isinstance(x, ast.Attribute) and x.attr == 'click'
                                  for x in ast.walk(n)))
        self.assertLess(loop.body.index(guard), first_click)
        tree.body = [guard]
        device = Mock()
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             appear=Mock(return_value=True), device=device)
        with self.assertRaisesRegex(RuntimeError, 'UR retirement'):
            exec(compile(tree, str(path), 'exec'), {
                'self': ui, 'KR_RETIRE_UR_WARNING': 'ur', 'RequestHumanTakeover': RuntimeError})
        device.click.assert_not_called()

    def test_warning_template_and_blank(self):
        button = Button(area=(489, 402, 607, 425), color=(0, 0, 0),
                        button=(489, 402, 607, 425),
                        file='./assets/kr/retire/KR_RETIRE_UR_WARNING.png')
        with Image.open(button.file) as image:
            frame = np.array(image.convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 30)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 30)))
        frame[402:425, 489:607] = 0
        self.assertFalse(frame.any())


if __name__ == '__main__':
    unittest.main()
