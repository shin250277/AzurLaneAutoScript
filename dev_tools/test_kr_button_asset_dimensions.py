"""Validate explicit KR Button files without importing game/device modules."""
import ast
from pathlib import Path
import unittest
from PIL import Image


def kr_buttons():
    root = Path(__file__).resolve().parents[1]
    for path in (root / 'module').rglob('assets.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != 'Button':
                continue
            values = {k.arg: ast.literal_eval(k.value) for k in node.keywords}
            files, areas = values.get('file'), values.get('area')
            if isinstance(files, dict) and 'kr' in files and isinstance(areas, dict) and 'kr' in areas:
                yield root / files['kr'], areas['kr']


class KrButtonAssetDimensionsTest(unittest.TestCase):
    def test_button_rois_are_inside_asset(self):
        for path, area in kr_buttons():
            with self.subTest(path=str(path)):
                with Image.open(str(path)) as image:
                    self.assertGreaterEqual(image.width, area[2])
                    self.assertGreaterEqual(image.height, area[3])


if __name__ == '__main__':
    unittest.main()
