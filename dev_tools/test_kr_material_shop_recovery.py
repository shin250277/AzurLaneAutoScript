"""Material shop chrome must not become the white main dock navigation."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock


class ShopRecoveryTest(unittest.TestCase):
    def test_public_header_fixtures_are_distinct_and_blank_rejected(self):
        import numpy as np
        from module.base.utils import load_image
        from module.ui.ui import KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER
        headers = (KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER)
        for header in headers:
            fixture = load_image(header.file)
            self.assertTrue(header.match(fixture, offset=(3, 3), similarity=0.95))
            self.assertFalse(header.match(np.zeros_like(fixture), offset=(3, 3), similarity=0.95))
            other = headers[1] if header is headers[0] else headers[0]
            self.assertFalse(other.match(fixture, offset=(3, 3), similarity=0.95))

    def test_shop_and_processing_only_leave_with_title_and_arrow(self):
        from module.ui.ui import UI, KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER
        from module.ui_white.assets import BACK_ARROW_WHITE
        for header in (KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER):
            for title, arrow in ((True, True), (True, False), (False, True)):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                    appear=lambda b, **kw: title if b is header else (
                        arrow if b is BACK_ARROW_WHITE else False))
                self.assertEqual(UI._handle_kr_island_character_back(ui), title and arrow)
                if title and arrow:
                    ui.device.click.assert_called_once_with(BACK_ARROW_WHITE)
                else:
                    ui.device.click.assert_not_called()

    def test_shop_headers_exclude_main_even_if_white_dock_matches(self):
        from module.ui.ui import UI, KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER
        from module.ui.page import page_main
        from module.ui_white.assets import MAIN_GOTO_DOCK_WHITE
        for header in (KR_ISLAND_SEED_HEADER, KR_ISLAND_PROCESSING_HEADER):
            ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                appear=lambda b, **kw: b in (header, MAIN_GOTO_DOCK_WHITE))
            self.assertFalse(UI.ui_page_appear(ui, page_main))

