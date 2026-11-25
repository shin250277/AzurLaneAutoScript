"""Disambiguate observed corn using its icon, not a fuzzy name guess."""
import subprocess
import sys
import unittest


class KoreanOrderIconTest(unittest.TestCase):
    def test_corn_requires_name_and_matching_row_icon(self):
        code = '''
import numpy as np
from PIL import Image
from module.island.korean_order_icons import resolve_order_icon
frame = np.array(Image.open('dev_tools/fixtures/kr_order_corn.png').convert('RGB'))
assert resolve_order_icon('옥수수', frame, 2) == 2001
assert resolve_order_icon('옥수수', frame, 0) is None
assert resolve_order_icon('옥수수', np.zeros_like(frame), 2) is None
assert resolve_order_icon('다른 품목', frame, 2) is None
assert resolve_order_icon(None, frame, 2) is None
assert resolve_order_icon('옥수수', frame, 3) is None
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
