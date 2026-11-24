import unittest
from unittest.mock import Mock

import numpy as np
from PIL import Image

import module.config.server as server
from module.island import assets
from module.island.transport import IslandTransport, SLOT_DELTA


class KoreanTransportBoardTest(unittest.TestCase):
    def test_claim_click_follows_matched_row(self):
        previous = server.server
        try:
            server.set_server('kr')
            claim = assets.ISLAND_TRANSPORT_CLAIM
            with Image.open(claim.file) as source:
                frame = np.roll(np.asarray(source.convert('RGB')), 2 * SLOT_DELTA, axis=0)
            for row in range(3):
                offset = (-5, row * SLOT_DELTA - 10, 5, row * SLOT_DELTA + 10)
                self.assertEqual(claim.match_template_color(frame, offset=offset), row == 2)
            self.assertGreater(claim.button[1], 500)
        finally:
            server.set_server(previous)

    def test_unconfirmed_list_does_not_repeat_input(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = range(4)
        ui.appear.return_value = ui.handle_transport_popup.return_value = False
        ui.is_in_transport_main.return_value = ui.appear_then_click.return_value = True
        self.assertFalse(IslandTransport.transport_list_open(ui))
        ui.appear_then_click.assert_called_once()
        ui.device.image_save.assert_called_once()
