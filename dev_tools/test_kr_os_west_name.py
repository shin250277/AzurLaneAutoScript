"""Observed west-sector OCR must not be replaced by an unrelated port."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock


class WestNameTest(unittest.TestCase):
    def parse(self, raw):
        path = Path('module/os/map_operation.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == 'get_zone_name' and any(
                      isinstance(d, ast.Call) and any(k.arg == 'SERVER'
                      and isinstance(k.value, ast.Str) and k.value.s == 'kr'
                      for k in d.keywords) for d in n.decorator_list))
        fn.decorator_list = []
        tree.body = [fn]
        ocr = Mock()
        ocr.ocr.return_value = raw
        scope = dict(Ocr=Mock(return_value=ocr), MAP_NAME='name')
        exec(compile(tree, str(path), 'exec'), scope)
        return scope['get_zone_name'](Mock())

    def test_observed_west_b_and_e(self):
        for letter in ('B', 'E'):
            self.assertEqual(self.parse('NASH-STII' + letter), 'NA Ocean W Sector ' + letter)

    def test_unknown_or_similar_region_is_not_guessed(self):
        for raw in ('NASH-IDIIAB', 'NASH-NSTIIB', 'NASH-STII', 'NASH-STIIBEXTRA'):
            self.assertEqual(self.parse(raw), raw)


if __name__ == '__main__':
    unittest.main()
