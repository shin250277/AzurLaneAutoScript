"""KR ingredient links can arrive directly at the material shop."""
from unittest.mock import Mock
import unittest


class MaterialShopProbeTest(unittest.TestCase):
    def test_info_dialog_routes_to_shop_without_reclicking_ingredient(self):
        from dev_tools.test_os_task_stop_boundaries import method
        navigate = method('module/island_handler/recipe.py', 'IslandRecipe',
                          'goto_ingredient_shop_page', Timer=Mock(),
                          page_island_shop='shop', ISLAND_INFO_GOTO_SHOP='info')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.side_effect = [[None], [None, None]]
        ui.ui_page_appear.return_value = False
        ui.appear.return_value = True
        ui.appear_then_click.side_effect = [True, False]
        ui._island_shop_side_navbar.get_info.return_value = (0, 2)
        self.assertTrue(navigate(ui, 'ingredient'))
        ui.device.click.assert_not_called()
        ui.appear_then_click.assert_called_with('info', offset=(20, 20), interval=2)

    def test_kr_direct_shop_arrival_does_not_wait_for_info_popup(self):
        from dev_tools.test_os_task_stop_boundaries import method
        navigate = method('module/island_handler/recipe.py', 'IslandRecipe',
                          'goto_ingredient_shop_page', Timer=Mock(),
                          page_island_shop='shop', ISLAND_INFO_GOTO_SHOP='info')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = [None]
        ui.ui_page_appear.return_value = True
        ui.appear.return_value = False
        ui.is_in_recipe_menu.return_value = False
        self.assertTrue(navigate(ui, 'ingredient'))
        ui.device.click.assert_not_called()
        ui.appear.assert_not_called()
