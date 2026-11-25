"""KR preparation recognition must tolerate a shifted label on the button."""
from pathlib import Path
import unittest

import numpy as np
from PIL import Image
from module.config import server
from module.combat.assets import BATTLE_PREPARATION
from module.base.button import Button


class PreparationTest(unittest.TestCase):
    def test_shifted_label_and_blank_negative(self):
        previous = server.server
        server.server = 'kr'
        try:
            button = Button(**{key: getattr(BATTLE_PREPARATION, 'raw_' + key)['kr']
                               for key in ('area', 'color', 'button', 'file')})
            path = Path(__file__).resolve().parents[1] / 'assets/kr/combat/BATTLE_PREPARATION.png'
            source = np.array(Image.open(path).convert('RGB'))
            shifted = np.zeros_like(source)
            # Live event label is shifted inside the otherwise unchanged button.
            shifted[618:647, 1073:1131] = source[614:643, 1060:1118]
            self.assertTrue(button.match(shifted, offset=(30, 20)))
            self.assertFalse(button.match(np.zeros_like(source), offset=(30, 20)))
        finally:
            server.server = previous


if __name__ == '__main__':
    unittest.main()
