"""Do not silently enter an unintended KR special zone."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class ZoneTypeTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/os/globe_operation.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'GlobeOperation')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'zone_type_select')]
        scope = dict(logger=Mock(), RequestHumanTakeover=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        self.select = scope['zone_type_select']
        self.handler = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                       zone_has_switch=lambda: False, get_zone_pinned_name=lambda: 'STRONGHOLD')

    def test_wrong_or_unknown_type_stops(self):
        for pinned in ['STRONGHOLD', 'ABYSSAL', '']:
            self.handler.get_zone_pinned_name = lambda: pinned
            with self.assertRaises(RuntimeError):
                self.select(self.handler)

    def test_matching_type_allowed(self):
        self.assertTrue(self.select(self.handler, types='STRONGHOLD'))

    def test_other_servers_unchanged(self):
        self.handler.config.SERVER = 'jp'
        self.assertTrue(self.select(self.handler))

    def test_normal_menu_template_does_not_match_fortress_card(self):
        import cv2
        import numpy as np
        from PIL import Image
        root = Path(__file__).resolve().parents[1]
        image = np.array(Image.open(str(root / 'assets/kr/os/SELECT_DANGEROUS.png')).convert('RGB'))
        card = np.array(Image.open(str(root / 'assets/kr/os/ZONE_STRONGHOLD.png')).convert('RGB'))
        template = image[315:337, 87:170]
        self.assertGreater(template.std(), 20)
        self.assertLess(cv2.matchTemplate(card, template, cv2.TM_CCOEFF_NORMED).max(), .75)

    def test_unknown_menu_times_out_without_selecting(self):
        path = Path(__file__).resolve().parents[1] / 'module/os/globe_operation.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'GlobeOperation')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'zone_select_enter')]
        scope = dict(ZONE_SWITCH='switch', GamePageUnknownError=RuntimeError)
        exec(compile(tree, str(path), 'exec'), scope)
        handler = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), loop=lambda timeout: range(3),
                                  is_in_zone_select=lambda: False, appear=Mock(return_value=False),
                                  device=SimpleNamespace(click=Mock()))
        with self.assertRaises(RuntimeError):
            scope['zone_select_enter'](handler)
        handler.device.click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
