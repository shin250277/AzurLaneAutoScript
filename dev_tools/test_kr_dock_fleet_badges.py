from pathlib import Path
import unittest

import numpy as np
from PIL import Image

import module.config.server as server
from module.retire.scanner import FleetScanner


class DockBadges(unittest.TestCase):
    def setUp(self):
        original = server.server
        self.addCleanup(server.set_server, original)
        server.set_server('kr')
        self.scan = FleetScanner()

    def test_fourteen_badges_in_card_order(self):
        fixture = Path(__file__).parent / 'fixtures/kr_dock_badge_digits.png'
        with Image.open(str(fixture)) as im:
            sheet = np.array(im.convert('RGB'))
        frame = np.zeros((720,1280,3), dtype=np.uint8)
        for i, grid in enumerate(self.scan.grids.buttons):
            x, y = grid.area[:2]
            frame[y+6:y+25,x+8:x+27] = sheet[:,19*i:19*(i+1)]
        self.assertEqual(self.scan._scan(frame), [1,2,1,2,1,2,3,2,3,2,2,1,3,1])

    def test_empty_cards_are_not_in_fleet(self):
        self.assertEqual(self.scan._scan(np.zeros((720,1280,3), dtype=np.uint8)), [0]*14)
