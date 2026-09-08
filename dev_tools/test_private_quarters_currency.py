"""Private quarters must not infer currency from the gift name alone."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class PrivateQuartersCurrencyTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/private_quarters/shop.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PQShop')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'shop_check_item')]
        scope = {'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['shop_check_item']
        self.shop = SimpleNamespace(config=SimpleNamespace(
            PrivateQuarters_BuyRoses=True, PrivateQuarters_BuyCake=False),
            _currency=100000, gems=940)

    def test_coin_roses_allowed(self):
        self.assertTrue(self.check(self.shop, SimpleNamespace(sub_genre='roses', cost='Coins')))

    def test_gem_roses_denied(self):
        self.assertFalse(self.check(self.shop, SimpleNamespace(sub_genre='roses', cost='Gems')))

    def test_unknown_currency_denied(self):
        self.assertFalse(self.check(self.shop, SimpleNamespace(sub_genre='roses', cost='Unknown')))

    def test_insufficient_coins_denied(self):
        self.shop._currency = 23999
        self.assertFalse(self.check(self.shop, SimpleNamespace(sub_genre='roses', cost='Coins')))

    def test_cake_disabled_even_with_sufficient_gems(self):
        self.assertFalse(self.check(self.shop, SimpleNamespace(sub_genre='cake', cost='Gems')))


class PurchaseDialogCurrencyTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'module/private_quarters/clerk.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PQShopClerk')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_kr_gift_purchase_is_coin')]
        scope = {'KR_GIFT_PURCHASE_COIN': 'coin_icon'}
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['_kr_gift_purchase_is_coin']
        self.ui = SimpleNamespace(appear=Mock(return_value=True))

    def test_roses_with_matching_coin_icon(self):
        self.assertTrue(self.check(self.ui, SimpleNamespace(sub_genre='roses', cost='Coins')))

    def test_missing_coin_icon_is_blocked(self):
        self.ui.appear.return_value = False
        self.assertFalse(self.check(self.ui, SimpleNamespace(sub_genre='roses', cost='Coins')))

    def test_gem_item_is_blocked_before_image_check(self):
        self.assertFalse(self.check(self.ui, SimpleNamespace(sub_genre='roses', cost='Gems')))
        self.ui.appear.assert_not_called()

    def test_other_gift_is_blocked(self):
        self.assertFalse(self.check(self.ui, SimpleNamespace(sub_genre='cake', cost='Coins')))
        self.ui.appear.assert_not_called()


if __name__ == '__main__':
    unittest.main()
