import unittest
from types import SimpleNamespace

from module.shop.shop_general import GeneralShop_250814 as GeneralShop


class GeneralShopBudget(unittest.TestCase):
    def setUp(self):
        self.ui = SimpleNamespace(_currency=550000, gems=1000000,
                                  config=SimpleNamespace(SERVER='kr', GeneralShop_UseGems=False,
                                                         GeneralShop_ConsumeCoins=True,
                                                         GeneralShop_BuySkinBox=False))

    def test_custom_coin_selection_checks_balance_even_above_threshold(self):
        for price, allowed in [(0, False), (1, True), (550000, True), (550001, False)]:
            with self.subTest(price=price):
                item = SimpleNamespace(price=price, cost='Coins')
                self.assertEqual(GeneralShop.shop_check_custom_item(self.ui, item), allowed)
        self.ui._currency = 549999
        self.assertFalse(GeneralShop.shop_check_custom_item(self.ui, SimpleNamespace(price=1, cost='Coins')))

    def test_diamonds_and_unknown_currency_excluded_in_both_selection_paths(self):
        for currency in ('Gems', 'Unknown'):
            item = SimpleNamespace(price=1, cost=currency)
            self.assertFalse(GeneralShop.shop_check_custom_item(self.ui, item))
            self.assertFalse(GeneralShop.shop_check_item(self.ui, item))
