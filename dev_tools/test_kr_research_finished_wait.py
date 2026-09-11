"""Keep animation waits, but recognize an already centered completed KR card."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class KrResearchFinishedWaitTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/research/research.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        tree.body = [next(n for n in ast.walk(tree)
                          if isinstance(n, ast.FunctionDef) and n.name == 'receive_6th_research')]
        self.timer = Mock()
        self.timer.reached.side_effect = [False, True]
        factory = Mock()
        factory.return_value.start.return_value = self.timer
        self.logger = Mock()
        scope = dict(Timer=factory, logger=self.logger)
        exec(compile(tree, str(path), 'exec'), scope)
        self.method = scope['receive_6th_research']
        self.ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'), device=Mock(),
            get_research_status=Mock(return_value=['detail', 'detail', 'unknown', 'detail', 'detail']),
            research_has_finished=Mock(return_value=True), _research_finished_index=2,
            research_receive=Mock(return_value=True), get_queue_slot=Mock(return_value=0),
            research_project_start=Mock())

    def test_centered_completed_card_does_not_timeout(self):
        self.assertTrue(self.method(self.ui))
        self.logger.warning.assert_not_called()
        self.ui.device.screenshot.assert_not_called()
        self.ui.research_receive.assert_called_once_with()

    def test_unknown_without_completion_keeps_timeout_and_diagnostic(self):
        self.ui.research_has_finished.return_value = False
        self.assertTrue(self.method(self.ui))
        self.logger.warning.assert_called_once()
        self.ui.device.image_save.assert_called_once_with('./log/kr_research_wait_timeout.png')
        self.ui.research_receive.assert_not_called()

    def test_off_center_completed_card_keeps_animation_wait(self):
        self.ui._research_finished_index = 1
        self.assertTrue(self.method(self.ui))
        self.logger.warning.assert_called_once()
        self.ui.device.screenshot.assert_called_once_with()

    def test_other_unknown_cards_keep_animation_wait(self):
        self.ui.get_research_status.return_value = ['unknown'] * 5
        self.assertTrue(self.method(self.ui))
        self.logger.warning.assert_called_once()

    def test_non_kr_path_unchanged(self):
        self.ui.config.SERVER = 'jp'
        self.assertTrue(self.method(self.ui))
        self.logger.warning.assert_called_once()
        self.ui.device.image_save.assert_not_called()

    def test_receive_failure_is_propagated(self):
        self.ui.research_receive.return_value = False
        self.assertFalse(self.method(self.ui))
        self.ui.research_project_start.assert_not_called()


if __name__ == '__main__':
    unittest.main()
