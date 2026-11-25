import unittest
import numpy as np
from module.base.utils import load_image
from module.base.button import Button


class KoreanMaterialDetailButtonTest(unittest.TestCase):
    def test_restart_only_closes_when_header_and_close_both_match(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from module.ui.ui import UI, KR_ISLAND_MATERIAL_DETAIL, KR_ISLAND_MATERIAL_DETAIL_CLOSE
        for title, close in ((True, True), (True, False), (False, True)):
            ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                appear=lambda b, **kw: title if b is KR_ISLAND_MATERIAL_DETAIL else (
                    close if b is KR_ISLAND_MATERIAL_DETAIL_CLOSE else False))
            self.assertEqual(UI._handle_kr_island_character_back(ui), title and close)
            if title and close:
                ui.device.click.assert_called_once_with(KR_ISLAND_MATERIAL_DETAIL_CLOSE)
            else:
                ui.device.click.assert_not_called()

    def test_korean_label_matches_and_japanese_label_does_not(self):
        frame = load_image('assets/kr/island_handler/ISLAND_INFO_GOTO_SHOP.png')
        area = (815, 472, 868, 495)
        kr = Button(area, (95, 201, 255), area,
                    file='assets/kr/island_handler/ISLAND_INFO_GOTO_SHOP.png')
        jp = Button(area, (95, 201, 255), area,
                    file='assets/jp/island_handler/ISLAND_INFO_GOTO_SHOP.png')
        self.assertTrue(kr.match(frame, offset=(20, 20)))
        self.assertFalse(jp.match(frame, offset=(20, 20)))
        self.assertFalse(kr.match(np.zeros_like(frame), offset=(20, 20)))

    def test_runtime_uses_korean_file(self):
        from module.island_handler.assets import ISLAND_INFO_GOTO_SHOP
        self.assertIn('/kr/', ISLAND_INFO_GOTO_SHOP.raw_file['kr'])
        self.assertIn('/jp/', ISLAND_INFO_GOTO_SHOP.raw_file['jp'])
