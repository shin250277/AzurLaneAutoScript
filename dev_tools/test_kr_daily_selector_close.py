import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class DailySelectorCloseTest(unittest.TestCase):
    def run_close(self, frames):
        state = {'frame': None}
        def loop(**kwargs):
            for frame in frames:
                state['frame'] = frame
                yield None
        ui = SimpleNamespace(device=Mock(), loop=loop, handle_get_items=Mock(),
                             match_template_color=lambda button, **kw: state['frame'] == button,
                             appear=lambda button, **kw: state['frame'] == button)
        run = method('module/daily/daily.py', 'Daily', 'close_korean_daily_selector',
                     DAILY_CHECK='list', KR_DAILY_SKIP='selector',
                     DAILY_ENTER_CHECK='detail', KR_DAILY_DISMISS='outside', BACK_ARROW='back')
        return ui, run

    def test_modal_then_detail_then_carousel(self):
        ui, run = self.run_close(['selector', 'detail', 'list'])
        self.assertTrue(run(ui))
        self.assertEqual([call[0][0] for call in ui.device.click.call_args_list], ['outside', 'back'])

    def test_already_returned_does_not_click(self):
        ui, run = self.run_close(['list'])
        self.assertTrue(run(ui))
        ui.device.click.assert_not_called()

    def test_unknown_view_never_clicks_or_assumes_return(self):
        ui, run = self.run_close(['unknown', 'unknown'])
        with self.assertRaises(TaskStopped):
            run(ui)
        ui.device.click.assert_not_called()

    def test_reward_is_not_followed_by_a_second_quick_battle(self):
        run = method('module/daily/daily.py', 'Daily', 'daily_enter',
                     DAILY_CHECK='list', DAILY_ENTER_CHECK='detail',
                     KR_DAILY_INFO_CONFIRM=SimpleNamespace(color=()),
                     KR_DAILY_SKIP='skip')
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr', Daily_UseDailySkip=True),
                             device=Mock(), appear=Mock(return_value=False),
                             match_template_color=lambda button, **kw: button == 'skip',
                             handle_get_items=Mock(side_effect=[True, False]),
                             image_color_count=Mock(return_value=False),
                             handle_combat_automation_confirm=Mock(return_value=False),
                             handle_daily_additional=Mock(return_value=False),
                             handle_popup_confirm=Mock(return_value=False),
                             close_korean_daily_selector=Mock(return_value=True))
        self.assertFalse(run(ui, 'mission'))
        ui.close_korean_daily_selector.assert_called_once()
        ui.device.click.assert_not_called()
        self.assertTrue(ui._kr_daily_skip_returned)


if __name__ == '__main__':
    unittest.main()
