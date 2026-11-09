"""KR shop reading must not guess names or shift later card positions."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from module.island_handler.shop import IslandShop


class KoreanShopIdentityTest(unittest.TestCase):
    def test_exact_korean_name_only(self):
        with patch('module.island_handler.shop.server.server', 'kr'):
            self.assertEqual(IslandShop.item_name_to_recipe_id(None, '메기 치어'), 111102)
            self.assertEqual(IslandShop.item_name_to_recipe_id(None, '메기치어'), 111102)
            for text in ('치어', '메기 치이', '', None):
                self.assertIsNone(IslandShop.item_name_to_recipe_id(None, text))

    def test_unknown_card_retains_its_position(self):
        ui = SimpleNamespace(device=SimpleNamespace(image=None),
                             _island_shop_item_name_ocr=Mock())
        ui._island_shop_item_name_ocr.ocr.return_value = ['', '메기 치어', '미확인', '치패']
        ui.item_name_to_recipe_id = lambda text: IslandShop.item_name_to_recipe_id(ui, text)
        with patch('module.island_handler.shop.server.server', 'kr'):
            self.assertEqual(IslandShop.island_shop_get_item_ids(ui), [None,111102,None,111101])

    def test_korean_ocr_backend_selected(self):
        ui = SimpleNamespace(_island_shop_item_name_grid=SimpleNamespace(buttons=[]))
        with patch('module.island_handler.shop.server.server', 'kr'):
            self.assertEqual(type(IslandShop._island_shop_item_name_ocr.fget(ui)).__name__,
                             'KoreanIslandShopNameOcr')

    def test_all_current_korean_purchase_names_are_unique(self):
        from module.island.data import DIC_ISLAND_SHOP_RECIPE
        with patch('module.island_handler.shop.server.server', 'kr'):
            for key, recipe in DIC_ISLAND_SHOP_RECIPE.items():
                self.assertEqual(IslandShop.item_name_to_recipe_id(None, recipe['name']['kr']), key)

    def test_ambiguous_dictionary_is_not_guessed(self):
        recipes = {1: {'name': {'kr': '씨앗'}}, 2: {'name': {'kr': '씨 앗'}}}
        with patch('module.island_handler.shop.server.server', 'kr'), patch(
                'module.island_handler.shop.DIC_ISLAND_SHOP_RECIPE', recipes):
            self.assertIsNone(IslandShop.item_name_to_recipe_id(None, '씨앗'))

    def test_foreign_name_matching_unchanged(self):
        with patch('module.island_handler.shop.server.server', 'jp'):
            self.assertEqual(IslandShop.item_name_to_recipe_id(None, '稚貝'), 111101)
