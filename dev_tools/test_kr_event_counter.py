"""Event-counter partial OCR must not crash or imply stock."""
import subprocess
import sys
import unittest


class EventCounterTest(unittest.TestCase):
    def test_partial_counters_and_kr_label_width(self):
        code = """
from unittest.mock import patch
import module.config.server as server
server.server = 'kr'
from module.shop_event.item import CounterOcr, COUNTER_LEFT_STRIP
from module.ocr.ocr import Ocr
ocr = CounterOcr([])
bad = ['/10', '5/', 'x/5', '14/5', '0/0', '5']
for text in bad:
    with patch.object(Ocr, 'ocr', return_value=text):
        assert ocr.ocr(None) == [0, 0], text
with patch.object(Ocr, 'ocr', return_value=bad + ['4/5', '10/10']):
    assert ocr.ocr(None) == [[0, 0]] * len(bad) + [[4, 5], [10, 10]]
assert COUNTER_LEFT_STRIP == 52
"""
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
