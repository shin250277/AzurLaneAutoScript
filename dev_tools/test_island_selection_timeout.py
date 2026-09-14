"""Unrecognized selection states should not click indefinitely."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class IslandSelectionTimeoutTest(unittest.TestCase):
    def test_selection_timeout_is_bounded_and_saves_frame(self):
        from module.island_handler.dock import IslandDock
        from module.exception import GameStuckError
        ui = SimpleNamespace(loop=Mock(return_value=iter([])), device=Mock(),
                             config=SimpleNamespace(SERVER='kr'))
        with self.assertRaises(GameStuckError):
            IslandDock.island_dock_select_one(ui, Mock())
        self.assertEqual(ui.loop.call_args[1]['timeout'], 8)
        ui.device.image_save.assert_called_once()

    def test_confirmation_timeout_is_bounded_and_saves_frame(self):
        from module.island_handler.dock import IslandDock
        from module.exception import GameStuckError
        ui = SimpleNamespace(loop=Mock(return_value=iter([])), device=Mock(),
                             config=SimpleNamespace(SERVER='kr'))
        with self.assertRaises(GameStuckError):
            IslandDock.island_dock_select_confirm(ui, Mock())
        self.assertEqual(ui.loop.call_args[1]['timeout'], 10)
        ui.device.image_save.assert_called_once()
