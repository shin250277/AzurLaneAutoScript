"""A completed card must not hide unfinished KR cards later in the list."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from dev_tools.test_kr_island_preflight import method


class SeasonCompleteScanTest(unittest.TestCase):
    def test_obtained_card_does_not_end_kr_scan(self):
        scroll = Mock()
        scroll.at_bottom.side_effect = [False, True]
        marker = Mock()
        marker.match.side_effect = [True, False, False, True]
        run = method('module/island/season_task.py', 'scan_all',
                     ISLAND_SEASON_TASK_SCROLL=scroll,
                     TEMPLATE_ISLAND_SEASON_TASK_OBTAINED=marker,
                     del_cached_property=Mock())
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             task_names=[None, 1], season_task_grid=SimpleNamespace(
                                 buttons=[SimpleNamespace(area=i) for i in range(2)]),
                             image_crop=lambda x, **kw: x, device=Mock())
        def next_page(**kwargs):
            ui.task_names = [2, None]
        scroll.next_page.side_effect = next_page
        self.assertEqual(run(ui), [1, 2])
        scroll.next_page.assert_called_once()
        ui.device.click.assert_not_called()
