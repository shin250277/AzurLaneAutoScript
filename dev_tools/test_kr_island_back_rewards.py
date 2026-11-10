"""Returning from a shop must not wait forever behind a purchase reward."""
import unittest
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method


class IslandBackRewardsTest(unittest.TestCase):
    def test_kr_back_services_existing_reward_handler(self):
        back = method('module/island/ui.py', 'IslandUI', 'ui_back', BACK_ARROW_WHITE='back')
        ui = Mock()
        ui.config.SERVER = 'kr'
        back(ui, 'recipe')
        options = ui.ui_click.call_args[1]
        self.assertEqual(options['additional'], ui.handle_island_additional)
        self.assertEqual(options['click_button'], 'back')
        self.assertEqual(options['check_button'], 'recipe')

    def test_other_servers_keep_original_navigation(self):
        back = method('module/island/ui.py', 'IslandUI', 'ui_back', BACK_ARROW_WHITE='back')
        ui = Mock()
        ui.config.SERVER = 'jp'
        back(ui, 'recipe')
        self.assertIsNone(ui.ui_click.call_args[1]['additional'])
