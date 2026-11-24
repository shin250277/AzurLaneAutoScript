import unittest
from unittest.mock import Mock

from module.dorm.buy_furniture import (BuyFurniture, DORM_FURNITURE_DETAILS_QUIT,
                                       KR_FURNITURE_DETAILS_QUIT)


class KoreanThemeOverviewTest(unittest.TestCase):
    def test_two_labels_required(self):
        for title, enter in [(True, False), (False, True), (True, True)]:
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.appear.side_effect = [title, enter]
            self.assertEqual(BuyFurniture._kr_theme_overview(ui), title and enter)

    def test_overview_set_tab_is_not_sheet_back_button(self):
        ui = Mock()
        ui._kr_theme_overview.return_value = True
        self.assertFalse(BuyFurniture._furniture_button_appear(
            ui, DORM_FURNITURE_DETAILS_QUIT, KR_FURNITURE_DETAILS_QUIT))
        ui.image_color_count.assert_not_called()

    def test_other_servers_do_not_read_kr_labels(self):
        ui = Mock()
        ui.config.SERVER = 'jp'
        self.assertFalse(BuyFurniture._kr_theme_overview(ui))
        ui.appear.assert_not_called()
