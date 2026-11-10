import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from module.ui.ui import UI
from module.ui.page import page_mail, page_research
from module.ui_white.assets import BACK_ARROW_WHITE


class KoreanMailNavigationTest(unittest.TestCase):
    def test_only_observed_korean_mail_back_overrides_legacy_link(self):
        old = object()
        for server, page, arrow in [('kr', page_mail, True), ('kr', page_mail, False),
                                    ('jp', page_mail, True), ('kr', page_research, True)]:
            with self.subTest(server=server, page=page, arrow=arrow):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                     appear=Mock(return_value=arrow))
                expected = BACK_ARROW_WHITE if server == 'kr' and page == page_mail and arrow else old
                self.assertIs(UI._kr_navigation_button(ui, page, old), expected)
