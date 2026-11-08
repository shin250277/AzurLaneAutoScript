import unittest
import subprocess
import sys


class CafeVariantTest(unittest.TestCase):
    def test_variant_matches_only_cafe_not_other_facilities(self):
        code = '''
import numpy as np
import module.config.server as server
server.server = 'kr'
from module.island import assets
from module.island.production import TEMPLATE_KR_PRODUCTION_CAFE_VARIANT as template
assert template.match(template.image)
blank = np.zeros((39, 265, 3), dtype=np.uint8)
assert not template.match(blank)
for name in ['FIELD','RANCH','FISHERY','MINE','WOOD','ORCHARD','NURSERY','KOI',
             'BEAR','EATERY','GRILL','LUMBER','MACHINERY','ELECTRONIC','CRAFTS']:
    other = getattr(assets, 'TEMPLATE_ISLAND_PRODUCTION_' + name)
    candidate = blank.copy()
    h, w = other.image.shape[:2]
    candidate[:h,:w] = other.image
    assert not template.match(candidate), name
    candidate = blank.copy()
    h, w = template.image.shape[:2]
    candidate[:h,:w] = template.image
    assert not other.match(candidate), name
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
