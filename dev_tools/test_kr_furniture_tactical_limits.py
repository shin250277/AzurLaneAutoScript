import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from module.dorm import buy_furniture as dorm
from module.exception import RequestHumanTakeover
from module.tactical import tactical_class as tactical


class KoreanPurchaseAndTrainingLimits(unittest.TestCase):
    def test_favourite_only_never_selects_from_unknown_or_unfiltered_dock(self):
        for state in ('off', 'unknown', 'on'):
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.config.AddNewStudent_Favorite = True
            ui.appear.return_value = True  # empty dock after positive filter
            with patch.object(tactical.DOCK_FAVOURITE, 'get', return_value=state):
                self.assertFalse(tactical.RewardTacticalClass.select_suitable_ship(ui))
            ui.dock_favourite_set.assert_called_once_with(enable=True)
            self.assertEqual(ui.appear.called, state == 'on')
            ui.device.click.assert_not_called()

    def test_bad_price_or_balance_never_confirms(self):
        for balance, price in [(0, 0), (200, 0), (0, 1), (149, 150)]:
            with self.subTest(balance=balance, price=price):
                ui = Mock()
                ui.config.SERVER = 'kr'
                with patch.object(dorm.OCR_FURNITURE_COIN, 'ocr', return_value=balance), \
                        patch.object(dorm.OCR_FURNITURE_PRICE, 'ocr', return_value=price), \
                        self.assertRaises(RequestHumanTakeover):
                    dorm.BuyFurniture.buy_furniture_once(ui, 'all')
                ui.buy_furniture_confirm.assert_not_called()

    def test_per_book_overflow_boundary(self):
        for tier, allowed in [(1, 200), (2, 200), (3, 100), (4, 100)]:
            for enabled in [False, True]:
                ui = Mock()
                ui.config.ControlExpOverflow_Enable = enabled
                setattr(ui.config, 'ControlExpOverflow_T%dAllow' % tier, allowed)
                limit = 800 + (allowed if enabled else 0)
                books = [SimpleNamespace(tier=tier, exp_value=n) for n in (100, limit, limit+1)]
                ui.books = tactical.SelectedGrids(books)
                with patch.object(tactical.SKILL_EXP, 'ocr', return_value=(5000, 800, 5800)):
                    tactical.RewardTacticalClass._tactical_books_filter_exp(ui)
                self.assertEqual(list(ui.books), books[:2])
