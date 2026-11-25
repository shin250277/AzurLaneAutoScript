import unittest
from unittest.mock import patch
import numpy as np
from pathlib import Path
from PIL import Image

from module.base.button import ButtonGrid
from module.shop.base import ShopItemGrid_250814


class PriceAnchorTest(unittest.TestCase):
    def check(self, server, template, anchored):
        grid = ButtonGrid(origin=(12, 0), delta=(100, 100), button_shape=(64, 64), grid_shape=(1, 1))
        g = ShopItemGrid_250814(grid, {}, cost_area=(-12, 115, 60, 155), price_area=(14, 121, 85, 150))
        im = np.full((170, 120, 3), 160, dtype=np.uint8)
        icon = np.random.RandomState(1).randint(0, 255, size=(20, 20, 3)).astype(np.uint8)
        im[121:141, 27:47] = icon
        g.cost_templates[template] = icon
        g.cost_templates_hit[template] = 0
        item = g.item_class(im, grid[0, 0])
        with patch('module.shop.base.server.server', server):
            self.assertEqual(g.match_cost_template(item), template)
        start = 47 if anchored else 26
        np.testing.assert_array_equal(item.crop(g.price_area), im[121:150, start:97])
        self.assertEqual(item.crop(g.cost_area).shape, (40, 72, 3))

    def test_localized_icons_only(self):
        for icon in ['Core_4', 'GuildCoins_6', 'GuildCoins_7']:
            self.check('kr', icon, True)
            self.check('jp', icon, False)
        self.check('kr', 'Gems', False)

    def test_real_currency_and_price_strips(self):
        with Image.open(str(Path(__file__).parent / 'fixtures/kr_shop_price_strips.png')) as f:
            pixels = np.asarray(f.convert('RGB'))
        self.assertEqual(pixels.shape, (200, 97, 3))
        grid = ButtonGrid(origin=(12, 0), delta=(100, 170), button_shape=(64, 64), grid_shape=(1, 5))
        im = np.full((850, 120, 3), 160, dtype=np.uint8)
        for row in range(5):
            im[170*row+115:170*row+155, :97] = pixels[40*row:40*(row+1)]
        g = ShopItemGrid_250814(grid, {}, cost_area=(-12, 115, 60, 155), price_area=(14, 121, 85, 150))
        g.load_cost_template_folder('./assets/shop/cost')
        with patch('module.shop.base.server.server', 'kr'):
            items = g.predict(im, name=False, amount=False, price=True, cost=True)
        self.assertEqual([(i.cost, i.price) for i in items], [
            ('Core', 35), ('Core', 1500), ('Core', 800), ('GuildCoins', 20), ('GuildCoins', 40)])
