"""Only acknowledge the specific KR auto-combat informational notice."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
import numpy as np
from PIL import Image
from module.base.button import Button


class NoticeTest(unittest.TestCase):
    def test_text_match_not_generic_button(self):
        b = Button(area=(363, 224, 643, 248), color=(0, 0, 0),
                   button=(575, 505, 700, 545),
                   file='./assets/kr/combat/KR_AUTOMATION_NOTICE.png')
        with Image.open(b.file) as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(b.match(frame, offset=(5, 5)))
        self.assertFalse(b.match(np.zeros_like(frame), offset=(5, 5)))
        frame[224:248, 363:643] = 0
        self.assertFalse(frame.any())

    def test_other_servers_and_missing_notice_do_not_click(self):
        path = Path('module/ui/ui.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'UI')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'handle_kr_automation_notice')]
        scope = {'KR_AUTOMATION_NOTICE': 'notice'}
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='jp'), appear_then_click=Mock())
        self.assertFalse(scope['handle_kr_automation_notice'](ui))
        ui.appear_then_click.assert_not_called()
        ui.config.SERVER = 'kr'
        ui.appear_then_click.return_value = False
        self.assertFalse(scope['handle_kr_automation_notice'](ui))
        ui.appear_then_click.return_value = True
        self.assertTrue(scope['handle_kr_automation_notice'](ui))


if __name__ == '__main__':
    unittest.main()
