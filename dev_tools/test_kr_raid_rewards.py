import unittest
from unittest.mock import Mock, patch

from module.exception import RequestHumanTakeover
from module.raid.kr_rewards import claim_visible_rewards


class RaidRewardsTest(unittest.TestCase):
    def ui(self):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.config.Campaign_Event = 'raid_20260827'
        ui.handle_get_items.return_value = False
        return ui

    def test_wrong_event_no_click(self):
        ui = self.ui()
        ui.config.Campaign_Event = 'unknown'
        with self.assertRaises(RequestHumanTakeover):
            claim_visible_rewards(ui)
        ui.device.click.assert_not_called()

    def test_missing_header_no_click(self):
        ui = self.ui()
        ui.appear.return_value = False
        with self.assertRaises(RequestHumanTakeover):
            claim_visible_rewards(ui)
        ui.device.click.assert_not_called()

    @patch('module.raid.kr_rewards.CLAIM')
    def test_disabled_claim_no_click(self, claim):
        ui = self.ui()
        claim.match_template_color.return_value = False
        claim_visible_rewards(ui)
        ui.device.click.assert_not_called()

    @patch('module.raid.kr_rewards.CLAIM')
    def test_active_claim_then_stop(self, claim):
        ui = self.ui()
        claim.match_template_color.side_effect = [True, False]
        claim_visible_rewards(ui)
        ui.device.click.assert_called_once_with(claim)

    def test_popup_loop_bounded(self):
        ui = self.ui()
        ui.handle_get_items.return_value = True
        with self.assertRaises(RequestHumanTakeover):
            claim_visible_rewards(ui)
        self.assertEqual(ui.handle_get_items.call_count, 12)
        ui.device.click.assert_not_called()
