"""Task changes may leave island selection without confirming a character."""
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class IslandCharacterRecoveryTest(unittest.TestCase):
    def test_back_requires_both_title_and_arrow(self):
        from module.ui.ui import UI
        from module.island_handler.assets import ISLAND_DOCK_CHECK
        from module.ui_white.assets import BACK_ARROW_WHITE
        for title, arrow in ((False, True), (True, False), (True, True)):
            with self.subTest(title=title, arrow=arrow):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'), device=Mock(),
                    appear=lambda b, **kw: title if b is ISLAND_DOCK_CHECK else arrow)
                self.assertEqual(UI._handle_kr_island_character_back(ui), title and arrow)
                if title and arrow:
                    ui.device.click.assert_called_once_with(BACK_ARROW_WHITE)
                else:
                    ui.device.click.assert_not_called()

    def test_other_servers_do_not_change_navigation(self):
        from module.ui.ui import UI
        self.assertFalse(UI._handle_kr_island_character_back(
            SimpleNamespace(config=SimpleNamespace(SERVER='jp'))))


if __name__ == '__main__':
    unittest.main()
