"""A research title behind a detail overlay is not the project list."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
import numpy as np


class ResearchDetailGuardTest(unittest.TestCase):
    def test_kr_queue_color_excludes_gold_card_background(self):
        from module.base.utils import get_color
        path = Path('module/research/rqueue.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == '_research_queue_add_available')]
        scope = dict(get_color=get_color,
                     RESEARCH_QUEUE_ADD=SimpleNamespace(button=(515, 550, 680, 615)))
        exec(compile(tree, str(path), 'exec'), scope)
        frame = np.full((720, 1280, 3), (220, 198, 120), dtype=np.uint8)
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             device=SimpleNamespace(image=frame))
        for color, expected in (((115, 164, 215), True), ((153, 160, 170), False)):
            with self.subTest(color=color):
                frame[559:604, 522:679] = color
                self.assertEqual(scope['_research_queue_add_available'](ui), expected)
        ui.config.SERVER = 'jp'
        frame[559:604, 522:679] = (115, 164, 215)
        self.assertFalse(scope['_research_queue_add_available'](ui))

    def test_queue_entry_closes_existing_kr_detail_first(self):
        path = Path('module/research/ui.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'queue_enter')]
        scope = dict(RESEARCH_GOTO_QUEUE='queue', page_research='page')
        exec(compile(tree, str(path), 'exec'), scope)
        for server, in_list in (('kr', False), ('kr', True), ('jp', False)):
            with self.subTest(server=server, in_list=in_list):
                events = []
                ui = SimpleNamespace(config=SimpleNamespace(SERVER=server),
                                     is_in_research=Mock(return_value=in_list),
                                     ui_page_appear=Mock(return_value=True),
                                     research_detail_quit=Mock(side_effect=lambda: events.append('close')),
                                     ui_click=Mock(side_effect=lambda *a, **k: events.append('queue')),
                                     is_in_queue=Mock())
                scope['queue_enter'](ui)
                self.assertEqual(events, ['close', 'queue'] if server == 'kr' and not in_list
                                 else ['queue'])

    def test_kr_unavailable_queue_preserves_project_and_defers(self):
        path = Path('module/research/rqueue.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                          and n.name == 'research_queue_add')]
        scope = dict(logger=Mock(), RESEARCH_QUEUE_ADD='queue')
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(config=Mock(SERVER='kr'), device=Mock(),
                             popup_interval_clear=Mock(), interval_clear=Mock(),
                             is_research_stabled=Mock(return_value=False),
                             appear=Mock(return_value=True),
                             _research_queue_add_available=Mock(return_value=False),
                             research_resume_interrupted_requirement=Mock(return_value=False),
                             research_detail_cancel=Mock(), research_detail_quit=Mock())
        ui.config.task_stop.side_effect = RuntimeError('task stopped')
        with self.assertRaisesRegex(RuntimeError, 'task stopped'):
            scope['research_queue_add'](ui)
        ui.device.image_save.assert_called_once_with('./log/kr_research_queue_unavailable.png')
        ui.research_detail_cancel.assert_not_called()
        ui.device.click.assert_not_called()
        ui.research_detail_quit.assert_called_once()
        ui.config.task_delay.assert_called_once_with(minute=30)

    def setUp(self):
        path = Path('module/research/ui.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ResearchUI')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'is_in_research')]
        scope = dict(page_research='page', RESEARCH_START='start',
                     RESEARCH_STOP='stop', RESEARCH_UNAVAILABLE='unavailable')
        exec(compile(tree, str(path), 'exec'), scope)
        self.check = scope['is_in_research']
        self.ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  ui_page_appear=Mock(return_value=True),
                                  appear=Mock(return_value=False))

    def test_detail_controls_exclude_visible_background_title(self):
        for control in ('start', 'stop', 'unavailable'):
            with self.subTest(control=control):
                self.ui.appear.side_effect = lambda button, **kwargs: button == control
                self.assertFalse(self.check(self.ui))

    def test_list_without_detail_controls_is_allowed(self):
        self.assertTrue(self.check(self.ui))

    def test_missing_title_is_not_the_list(self):
        self.ui.ui_page_appear.return_value = False
        self.assertFalse(self.check(self.ui))

    def test_other_servers_keep_original_page_detection(self):
        self.ui.config.SERVER = 'jp'
        self.assertTrue(self.check(self.ui, interval=3))
        self.ui.appear.assert_not_called()
        self.ui.ui_page_appear.assert_called_once_with('page', offset=(20, 20), interval=3)


if __name__ == '__main__':
    unittest.main()
