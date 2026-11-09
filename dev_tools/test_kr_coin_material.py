import unittest
from module.island_handler.kr_coin_material import purchase_allowed, material_shortfall


class CoinMaterialTest(unittest.TestCase):
    def test_actual_quantity_digits(self):
        import numpy as np
        from module.base.utils import load_image
        from module.island_handler.kr_coin_material import read_quantity
        for value in (1, 14):
            frame = np.full((720, 1280, 3), 255, dtype=np.uint8)
            frame[360:382,756:850] = load_image(
                'dev_tools/fixtures/kr_material_quantity_%s.png' % value)
            self.assertEqual(read_quantity(frame), value)

    def test_quantity_disagreement_or_blank_never_authorizes(self):
        from unittest.mock import patch
        from module.island_handler.kr_coin_material import read_quantity
        for values in ([14, 4], [0, 0], [101, 101]):
            with patch('module.ocr.ocr.Digit.ocr', side_effect=values):
                self.assertEqual(read_quantity(None), 0)

    def test_coin_marker_is_required_independently_of_purchase_text(self):
        import numpy as np
        from module.base.utils import load_image
        from module.island_handler.kr_coin_material import AREAS, marker, dialog_evidence
        image = np.zeros((720, 1280, 3), dtype=np.uint8)
        for name, (x1,y1,x2,y2) in AREAS.items():
            image[y1:y2,x1:x2] = load_image('assets/kr/island_material/%s.png' % name)
            self.assertTrue(marker(image, name))
        x1,y1,x2,y2 = AREAS['coin']
        image[y1:y2,x1:x2] = 0
        self.assertIsNone(dialog_evidence(image))

    def test_replenishment_requires_exact_inventory_increment(self):
        from unittest.mock import Mock, patch
        from module.island_handler.kr_coin_material import replenish_for_recipe
        from module.exception import RequestHumanTakeover
        ui = Mock()
        ui.get_recipe_ingredient_grids.return_value.buttons = ['ingredient']
        ui.set_recipe.return_value = True
        ui.set_recipe_batch_count.return_value = True
        ui.get_recipe_ingredient_counters.return_value = [(9, 9, 0)]
        with patch('module.island_handler.kr_coin_material.buy_material', return_value=True) as buy:
            self.assertEqual(replenish_for_recipe(ui, 101001, {1000: 9}, [(0,9,-9)], {}, 1, None), [(9,9,0)])
            buy.assert_called_once_with(ui, 1000, 9, 'ingredient')
            ui.get_recipe_ingredient_counters.return_value = [(10,9,1)]
            with self.assertRaises(RequestHumanTakeover):
                replenish_for_recipe(ui, 101001, {1000: 9}, [(0,9,-9)], {}, 1, None)

    def test_surplus_and_composite_recipes_remain_owned_only(self):
        from unittest.mock import Mock, patch
        from module.island_handler.kr_coin_material import replenish_for_recipe
        with patch('module.island_handler.kr_coin_material.buy_material') as buy:
            replenish_for_recipe(Mock(), 101001, {1000:9}, [(0,9,-9)], {}, 1, 'buffer_surplus')
            replenish_for_recipe(Mock(), 1, {1000:9, 2000:1}, [(0,9,-9),(0,1,-1)], {}, 1, None)
            buy.assert_not_called()

    def test_resume_closes_preview_without_buying(self):
        from unittest.mock import Mock, patch
        from module.island_handler.kr_coin_material import recover_preview
        ui = Mock()
        ui.device.image = None
        ui.loop.return_value = iter([None])
        ui.ui_page_appear.return_value = True
        with patch('module.island_handler.kr_coin_material.marker', side_effect=[True, True, False]):
            recover_preview(ui)
        self.assertEqual(ui.device.click.call_count, 1)
        self.assertEqual(ui.device.click.call_args[0][0].name, 'KR_MATERIAL_PREVIEW_CLOSE')

    def test_dialog_item_label_without_ocr_guess(self):
        from unittest.mock import patch
        from module.base.utils import load_image
        from module.island_handler.korean_ocr import KoreanIslandShopNameOcr
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda frames: [[] for _ in frames]
            self.assertEqual(KoreanIslandShopNameOcr([]).ocr(
                [load_image('dev_tools/fixtures/kr_wheat_seed_dialog.png')], direct_ocr=True), ['밀 씨앗'])

    def test_exact_coin_price_and_quantity(self):
        self.assertTrue(purchase_allowed({1: 20}, '밀 씨앗', 9, 180,
                                         '밀씨앗', 9, True))

    def test_reject_currency_identity_amount_price_and_missing_coin(self):
        base = [{1: 20}, '밀 씨앗', 9, 180, '밀씨앗', 9, True]
        for index, value in [(0, {2: 20}), (0, {1: 20, 2: 1}), (1, '옥수수 씨앗'),
                             (2, 8), (3, 20), (5, 0), (5, True), (6, False)]:
            args = list(base)
            args[index] = value
            self.assertFalse(purchase_allowed(*args))

    def test_shortfall_preserves_reserves_and_bounds_single_purchase(self):
        self.assertEqual(material_shortfall(0, 9, 0, 1), 9)
        self.assertEqual(material_shortfall(10, 9, 5, 2), 13)
        self.assertEqual(material_shortfall(40, 9, 5, 2), 0)
        self.assertIsNone(material_shortfall(0, 9, 0, float('inf')))
        self.assertIsNone(material_shortfall(0, 9, 0, 100))
        self.assertIsNone(material_shortfall(0, 9, -1, 1))

    def test_purchase_confirms_once_only_after_full_evidence(self):
        from unittest.mock import Mock, patch
        from module.island_handler.kr_coin_material import buy_material
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.side_effect = lambda **kwargs: iter([None, None])
        ui.goto_ingredient_shop_page.return_value = True
        ui.island_shop_get_item_ids.return_value = [None, 411000]
        ui._island_shop_item_grid.buttons = ['wrong', 'wheat']
        ui.island_shop_get_currency.side_effect = [{1: 1000}, {1: 820}]
        ui.ui_page_appear.return_value = True
        with patch('module.island_handler.kr_coin_material.dialog_evidence', return_value=('밀 씨앗', 9, 180)), patch('module.island_handler.kr_coin_material.marker', return_value=False):
            self.assertTrue(buy_material(ui, 1000, 9, 'ingredient'))
        self.assertEqual(ui.device.click.call_count, 2)
        self.assertEqual(ui.device.click.call_args_list[0][0], ('wheat',))

    def test_wrong_item_never_confirms(self):
        from unittest.mock import Mock, patch
        from module.island_handler.kr_coin_material import buy_material
        from module.exception import RequestHumanTakeover
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.side_effect = lambda **kwargs: iter([None])
        ui.goto_ingredient_shop_page.return_value = True
        ui.island_shop_get_item_ids.return_value = [411000]
        ui._island_shop_item_grid.buttons = ['wheat']
        ui.island_shop_get_currency.return_value = {1: 1000}
        with patch('module.island_handler.kr_coin_material.dialog_evidence', return_value=('옥수수 씨앗', 9, 180)):
            with self.assertRaises(RequestHumanTakeover):
                buy_material(ui, 1000, 9, 'ingredient')
        ui.device.click.assert_called_once_with('wheat')
