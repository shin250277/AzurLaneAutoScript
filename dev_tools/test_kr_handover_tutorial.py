"""Only the observed KR handover tutorial may be dismissed."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class HandoverTutorialTest(TestCase):
    def test_exact_tutorial_only(self):
        run = method('module/handler/info_handler.py', 'InfoHandler',
                     'handle_kr_handover_tutorial', KR_HANDOVER_TUTORIAL=SimpleNamespace(name='tutorial'),
                     KR_HANDOVER_TUTORIAL_2=SimpleNamespace(name='tutorial2'),
                     KR_HANDOVER_TUTORIAL_3=SimpleNamespace(name='tutorial3'))
        for server, visible in [('kr', True), ('kr', False), ('jp', True)]:
            obj = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                  appear=Mock(return_value=visible), device=Mock())
            self.assertEqual(run(obj), server == 'kr' and visible)
            self.assertEqual(obj.device.click.call_count, int(server == 'kr' and visible))
            if server != 'kr':
                obj.appear.assert_not_called()
            elif visible:
                run(obj)
                run(obj)
                with self.assertRaises(TaskStopped):
                    run(obj)
                self.assertEqual(obj.device.click.call_count, 3)
