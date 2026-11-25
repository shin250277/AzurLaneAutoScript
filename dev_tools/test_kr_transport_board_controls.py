import unittest
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image

import module.config.server as server
from module.island import assets
from module.island.transport import IslandTransport, KR_TRANSPORT_SWAP_QUESTION, SLOT_DELTA
from module.island_handler.exchange import (
    IslandExchange, KR_ISLAND_ACTION_ACCEPT, KR_FISH_PROCESS_QUESTION,
)


class KoreanTransportBoardTest(unittest.TestCase):
    def test_action_questions_do_not_match_each_other(self):
        questions = (KR_TRANSPORT_SWAP_QUESTION, KR_FISH_PROCESS_QUESTION)
        for question in questions:
            with Image.open(question.file) as mask:
                frame = np.array(mask.convert('RGB'))
            for candidate in questions:
                self.assertEqual(candidate.match_template_color(frame, offset=(4, 4)), candidate is question)

    def test_exchange_needs_expected_quantity_and_specific_question(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = range(4)
        ui.handle_island_get_items.return_value = ui.handle_island_level_up.return_value = False
        ui.appear_then_click.return_value = True
        ui.match_template_color.side_effect = lambda button, **kw: button is KR_ISLAND_ACTION_ACCEPT
        with patch('module.island_handler.exchange.read_fish_meat', side_effect=[(28, 0), (28, 60), (28, 60), (28, 60)]):
            self.assertIsNone(IslandExchange._exchange_confirm(ui, 2521, 28, 60))
        ui.appear_then_click.assert_called_once()
        ui.handle_island_popup_confirm.assert_not_called()
        ui.device.click.assert_not_called()

    def test_top_retries_one_unmoved_drag_on_kr(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        bottom, top = [Mock(index=3)], [Mock(index=1)]
        ui.transport_list_wait_rows.return_value = bottom
        ui.transport_list_drag.side_effect = [bottom, top]
        self.assertEqual(IslandTransport.transport_list_top(ui), top)
        self.assertEqual(ui.transport_list_drag.call_count, 2)

    def test_list_modal_is_not_the_primary_board(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.appear.return_value = True
        self.assertFalse(IslandTransport.is_in_transport_main(ui))
        ui.appear.assert_called_once_with(assets.ISLAND_TRANSPORT_LIST_CHECK, offset=(10, 10))
        ui.ui_page_appear.assert_not_called()

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
