import unittest
from unittest.mock import Mock
from types import SimpleNamespace
from dev_tools.test_kr_island_preflight import method


class SeasonProgressTest(unittest.TestCase):
    def run_pages(self, pages, server='kr'):
        scroll = Mock()
        scroll.name = 'ISLAND_SEASON_TASK_SCROLL'
        scroll.at_bottom.side_effect = [False] * (len(pages)-1) + [True]
        ui = SimpleNamespace(config=SimpleNamespace(SERVER=server), device=Mock(),
                             image_crop=Mock(), task_names=pages[0],
                             season_task_grid=SimpleNamespace(buttons=[SimpleNamespace(area=())]))
        pending = iter(pages[1:])
        scroll.next_page.side_effect = lambda **kw: setattr(ui, 'task_names', next(pending))
        run = method('module/island/season_task.py', 'scan_all',
                     ISLAND_SEASON_TASK_SCROLL=scroll, del_cached_property=Mock(),
                     TEMPLATE_ISLAND_SEASON_TASK_OBTAINED=Mock(match=Mock(return_value=False)))
        run(ui)
        ui.device.test_scroll = scroll
        return ui.device

    def test_only_new_identified_page_removes_scroll_history(self):
        device = self.run_pages([[1], [1], [2]])
        self.assertEqual(device.click_record_remove.call_count, 2)
        device.click_record_remove.assert_called_with('ISLAND_SEASON_TASK_SCROLL')
        device.click_record_clear.assert_not_called()

    def test_other_servers_unchanged(self):
        self.run_pages([[1], [2]], 'jp').click_record_remove.assert_not_called()

    def test_korean_scroll_uses_overlapping_half_page(self):
        for server, expected in [('kr', 0.4), ('jp', 0.8)]:
            scroll = self.run_pages([[1], [2]], server).test_scroll
            self.assertEqual(scroll.next_page.call_args[1]['page'], expected)
