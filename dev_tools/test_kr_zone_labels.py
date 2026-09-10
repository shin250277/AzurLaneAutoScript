"""Korean zone labels must not fall back to Japanese glyphs."""
import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
from PIL import Image
from module.base.button import Button
from module.os.assets import SELECT_OBSCURE, SELECT_SAFE, ZONE_OBSCURE


class KrZoneLabelsTest(unittest.TestCase):
    def test_korean_heading_wins_over_shared_dangerous_subtitle(self):
        path = Path('module/os/globe_operation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'GlobeOperation')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'get_zone_pinned')]
        dangerous, obscure = Mock(), Mock()
        scope = dict(ZONE_TYPES=[dangerous, obscure], ZONE_DANGEROUS=dangerous,
                     ZONE_OBSCURE=obscure, ASSETS_PINNED_ZONE=[])
        exec(compile(tree, str(path), 'exec'), scope)
        handler = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), appear=lambda *a, **k: True)
        self.assertIs(scope['get_zone_pinned'](handler), obscure)
        handler.config.SERVER = 'jp'
        self.assertIs(scope['get_zone_pinned'](handler), dangerous)

    def test_explicit_korean_templates(self):
        for asset in (SELECT_OBSCURE, SELECT_SAFE, ZONE_OBSCURE):
            self.assertIn('kr', asset.raw_file, asset.name)

    def test_dropdown_labels_are_distinct(self):
        assets = (SELECT_OBSCURE, SELECT_SAFE)
        for asset in assets:
            button = Button(area=asset.raw_area['kr'], color=asset.raw_color['kr'],
                            button=asset.raw_button['kr'], file=asset.raw_file['kr'])
            frame = np.asarray(Image.open(button.file).convert('RGB'))
            self.assertTrue(button.match(frame, offset=(20, 200), similarity=.75))
            self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 200), similarity=.75))
            other = assets[1] if asset is assets[0] else assets[0]
            other_frame = np.asarray(Image.open(other.raw_file['kr']).convert('RGB'))
            self.assertFalse(button.match(other_frame, offset=(20, 200), similarity=.75))


if __name__ == '__main__':
    unittest.main()
