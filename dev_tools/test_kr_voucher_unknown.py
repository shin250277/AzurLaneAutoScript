"""Unknown voucher items must not be reported as verified absence."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class VoucherUnknownTest(unittest.TestCase):
    def test_kr_single_exchange_confirmation_branch(self):
        from module.shop.shop_voucher import VoucherShop, KR_VOUCHER_EXCHANGE
        shop = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                               appear=Mock(return_value=False),
                               handle_popup_confirm=Mock(return_value=False),
                               appear_then_click=Mock(return_value=True))
        self.assertTrue(VoucherShop.shop_buy_handle(shop, object()))
        shop.appear_then_click.assert_called_once_with(
            KR_VOUCHER_EXCHANGE, offset=(-20, -140, 20, -100), interval=3)

    def test_exchange_label_matches_shifted_button_and_not_blank(self):
        from module.shop.shop_voucher import KR_VOUCHER_EXCHANGE
        from module.base.utils import load_image
        import numpy as np
        source = load_image('assets/kr/shop/SHOP_BUY_CONFIRM_AMOUNT.png')
        image = np.zeros_like(source)
        image[502:537, 750:821] = source[620:655, 755:826]
        self.assertTrue(KR_VOUCHER_EXCHANGE.match(image, offset=(-20, -140, 20, -100)))
        self.assertFalse(KR_VOUCHER_EXCHANGE.match(np.zeros_like(source), offset=(-20, -140, 20, -100)))

    def test_kr_grid_matches_observed_five_column_layout(self):
        from module.shop.shop_voucher import VoucherShop
        import numpy as np
        grid = VoucherShop.shop_grid.func(SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'),
            _get_vouchers=lambda: np.array([[0, 27], [0, 235]])))
        self.assertEqual(tuple(grid.origin), (305, 200))
        self.assertEqual(tuple(grid.delta), (189.5, 208))

    def run_shop(self, server, names, selected=None):
        tree = ast.parse(Path('module/shop/shop_voucher.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'VoucherShop')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'run_once')
        scope = {'logger': Mock()}
        exec(compile(ast.Module(body=[method]), '<voucher>', 'exec'), scope)
        shop = SimpleNamespace(
            config=SimpleNamespace(SERVER=server), device=Mock(), _currency=100,
            wait_until_voucher_appear=Mock(), shop_currency=Mock(),
            shop_get_items=Mock(return_value=[SimpleNamespace(name=n) for n in names]),
            shop_get_item_to_buy=Mock(return_value=selected), shop_buy_execute=Mock())
        result = scope['run_once'](shop)
        return shop, scope['logger'], result

    def test_kr_unknown_retains_diagnostic_without_purchase(self):
        shop, logger, result = self.run_shop('kr', ['26', 'Coin'])
        self.assertFalse(result)
        shop.device.image_save.assert_called_once_with('./log/kr_voucher_unknown.png')
        shop.shop_buy_execute.assert_not_called()
        logger.warning.assert_called()

    def test_kr_known_absence_does_not_capture(self):
        shop, logger, result = self.run_shop('kr', ['Coin'])
        self.assertFalse(result)
        shop.device.image_save.assert_not_called()

    def test_other_server_unchanged(self):
        shop, logger, result = self.run_shop('jp', ['26'])
        self.assertFalse(result)
        shop.device.image_save.assert_not_called()

    def test_known_archive_purchase_unchanged(self):
        selected = object()
        shop, logger, result = self.run_shop('kr', ['LoggerArchiveT2'], selected)
        self.assertTrue(result)
        shop.shop_buy_execute.assert_called_once_with(selected)
        shop.device.image_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
