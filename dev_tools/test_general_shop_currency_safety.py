"""Offline regression for the no-premium general-shop configuration.

This checks decision logic, not currency-template accuracy on live shop cards.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class GeneralShopCurrencySafetyTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/shop/shop_general.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                   and node.name == 'GeneralShop_250814')
        tree.body = [node for node in cls.body if isinstance(node, ast.FunctionDef)
                     and node.name in ('shop_check_item', 'shop_check_custom_item')]
        scope = {'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['shop_check_item']
        self.custom = scope['shop_check_custom_item']
        self.shop = SimpleNamespace(
            config=SimpleNamespace(GeneralShop_UseGems=False,
                                   GeneralShop_ConsumeCoins=True,
                                   GeneralShop_BuySkinBox=True),
            _currency=600000, gems=100000)

    def item(self, cost, price=7000):
        return SimpleNamespace(cost=cost, price=price, amount=1,
                               is_known_item=lambda: False)

    def test_gems_denied_even_with_sufficient_balance(self):
        self.assertFalse(self.check(self.shop, self.item('Gems')))

    def test_unknown_currency_denied(self):
        for cost in ('Unknown', '', None):
            with self.subTest(cost=cost):
                self.assertFalse(self.check(self.shop, self.item(cost)))

    def test_custom_coin_consumption_and_skin_box_cannot_bypass_currency(self):
        for cost in ('Gems', 'Unknown', '', None):
            with self.subTest(cost=cost):
                self.assertFalse(self.custom(self.shop, self.item(cost)))

    def test_coin_purchase_requires_sufficient_balance(self):
        self.assertTrue(self.check(self.shop, self.item('Coins', 600000)))
        self.assertFalse(self.check(self.shop, self.item('Coins', 600001)))


if __name__ == '__main__':
    unittest.main()
