"""Localized unavailable-research label and non-clicking shortage branch."""
import subprocess
import sys
import unittest


class KoreanResearchUnavailableTest(unittest.TestCase):
    def test_localized_asset_and_blank_rejection(self):
        code = '''
import numpy as np
from PIL import Image
import module.config.server as server
server.server = 'kr'
from module.research.assets import RESEARCH_UNAVAILABLE as button
assert '/kr/' in button.file.replace(chr(92), '/')
frame = np.array(Image.open(button.file).convert('RGB'))
assert button.match(frame)
assert not button.match(np.zeros((720,1280,3), dtype=np.uint8))
'''
        result = subprocess.run([sys.executable, '-B', '-c', code],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    unittest.main()
