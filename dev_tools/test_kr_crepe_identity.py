import unittest
from module.island.data import DIC_ISLAND_ITEM, DIC_ISLAND_RECIPE


class CrepeIdentityTest(unittest.TestCase):
    def test_observed_korean_recipe_and_product_agree(self):
        self.assertEqual(DIC_ISLAND_ITEM[3026]['name']['kr'], '바나나 크레이프')
        self.assertEqual(DIC_ISLAND_RECIPE[603005]['name']['kr'], DIC_ISLAND_ITEM[3026]['name']['kr'])
