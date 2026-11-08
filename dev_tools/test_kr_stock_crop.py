import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from module.base.utils import load_image
from module.island_handler.korean_stock import KoreanRecipeStockDigit
from dev_tools.test_os_task_stop_boundaries import method


class StockCropTest(unittest.TestCase):
    def test_kr_repeated_final_digit_retains_bottom_context(self):
        frame = load_image('dev_tools/fixtures/kr_stock_repeated_digits.png')
        ocr = KoreanRecipeStockDigit([], lang='cnocr', letter=(80, 80, 80), threshold=160)
        run = method('module/island_handler/recipe.py', 'IslandRecipe', 'get_recipe_product_stocks',
                     server=SimpleNamespace(server='kr'), RECIPE_PRODUCT_STOCK_OCR=ocr,
                     RECIPE_PRODUCT_STOCK_AREA=(212, 92, 275, 110))
        grid = Mock()
        grid.crop.side_effect = lambda a, **kw: SimpleNamespace(buttons=[
            SimpleNamespace(area=(0, 0, a[2]-a[0], a[3]-a[1]))])
        ui = SimpleNamespace(recipe_grid=grid, image_crop=lambda a, **kw: frame[:a[3], :a[2]])
        self.assertEqual(run(ui), [1311])
        grid.crop.assert_called_once_with((212, 92, 275, 114), name='RECIPE_PRODUCT_STOCK_GRID')

    def test_other_servers_keep_original_area(self):
        run = method('module/island_handler/recipe.py', 'IslandRecipe', 'get_recipe_product_stocks',
                     server=SimpleNamespace(server='jp'), RECIPE_PRODUCT_STOCK_OCR=Mock(),
                     RECIPE_PRODUCT_STOCK_AREA=(212, 92, 275, 110))
        grid = Mock()
        grid.crop.return_value.buttons = []
        run(SimpleNamespace(recipe_grid=grid))
        grid.crop.assert_called_once_with((212, 92, 275, 110), name='RECIPE_PRODUCT_STOCK_GRID')
