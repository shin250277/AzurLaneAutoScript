import unittest
from unittest.mock import Mock, patch

from module.minigame.minigame import Minigame


class KoreanArcadeBalance(unittest.TestCase):
    def run_room(self, balances):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = []
        ui.collect_coin.return_value = False
        ui.get_coin_amount.side_effect = balances
        with patch('module.minigame.new_year_challenge.NewYearChallenge') as game:
            game.return_value.minigame_run.return_value = True
            Minigame.run(ui)
        ui.config.task_delay.assert_called_once_with(server_update=True)
        return game.return_value.minigame_run.call_count

    def test_stalled_balance_requires_two_completed_games_and_fresh_read(self):
        self.assertEqual(self.run_room([1, 1, 1, 1]), 2)
        self.assertEqual(self.run_room([1, 1, 1, 0]), 2)

    def test_progress_or_stale_read_does_not_stop_play(self):
        self.assertEqual(self.run_room([3, 2, 1, 0]), 3)
        self.assertEqual(self.run_room([3, 3, 3, 2, 1, 0]), 4)
