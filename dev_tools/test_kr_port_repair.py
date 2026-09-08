"""The KR repair confirmation must follow a repair request."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class PortRepairTest(unittest.TestCase):
    def test_defeat_templates_are_distinct(self):
        import cv2
        import numpy as np
        from PIL import Image
        root = Path(__file__).resolve().parents[1]
        cases = [('DEFEAT_RESULT', (230, 220, 551, 293)),
                 ('DEFEAT_SUMMARY', (28, 58, 311, 119))]
        images = [np.array(Image.open(str(root / 'assets/kr/ui' / (name + '.png'))).convert('RGB'))
                  for name, _ in cases]
        for index, (_, (x, y, right, bottom)) in enumerate(cases):
            template = images[index][y:bottom, x:right]
            self.assertGreater(template.std(), 20)
            # Large white defeat lettering, not a mostly dark ship-result row.
            self.assertGreater((template.min(axis=2) > 180).mean(), .20)
            self.assertGreater(cv2.matchTemplate(images[index], template, cv2.TM_CCOEFF_NORMED).max(), .99)
            self.assertLess(cv2.matchTemplate(images[1-index], template, cv2.TM_CCOEFF_NORMED).max(), .85)

    def test_repair_requested_before_color_confirmation(self):
        path = Path(__file__).resolve().parents[1] / 'module/os_handler/port.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PortHandler')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'port_dock_repair')]
        confirm = SimpleNamespace(color=(90, 137, 195))
        scope = dict(PORT_GOTO_DOCK='enter', PORT_CHECK='port', PORT_DOCK_CHECK='repair',
                     KR_PORT_DOCK_CONFIRM=confirm)
        exec(compile(tree, str(path), 'exec'), scope)
        events = []
        handler = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'), loop=lambda: range(4), ui_click=Mock(), ui_back=Mock(),
            info_bar_count=Mock(return_value=0), appear=Mock(return_value=True),
            handle_popup_confirm=Mock(return_value=False), image_color_count=Mock(return_value=True),
            get_interval_timer=Mock(return_value=SimpleNamespace(reached=lambda: True)), interval_reset=Mock(),
            appear_then_click=Mock(side_effect=lambda *a, **kw: events.append('request') or True),
            device=SimpleNamespace(click=Mock(side_effect=lambda *a: events.append('confirm'))))
        scope['port_dock_repair'](handler)
        self.assertEqual(events, ['request', 'confirm'])


if __name__ == '__main__':
    unittest.main()
