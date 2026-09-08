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


if __name__ == '__main__':
    unittest.main()
