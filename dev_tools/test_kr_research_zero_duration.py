import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest


class ResearchZeroDurationTest(unittest.TestCase):
    def test_expired_unmet_research_attempts_recovery_then_yields(self):
        path = Path('module/research/selector.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ResearchSelector')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == '_research_detail_detect')]
        timer = Mock()
        timer.start.return_value = timer
        timer.reached.return_value = True
        detector = Mock(return_value=SimpleNamespace(duration='0'))
        scope = dict(Timer=Mock(return_value=timer), logger=Mock(), research_jp_detect=detector)
        exec(compile(tree, str(path), 'exec'), scope)
        ui = SimpleNamespace(config=Mock(SERVER='kr'), device=Mock(), info_bar_count=lambda: 0,
                             research_resume_interrupted_requirement=Mock(return_value=False),
                             research_detail_quit=Mock())
        ui.config.task_stop.side_effect = RuntimeError('yield task')
        # Bound the old implementation so RED fails instead of hanging.
        detector.side_effect = [SimpleNamespace(duration='0'), RuntimeError('unbounded retry')]
        with self.assertRaisesRegex(RuntimeError, 'yield task'):
            scope['_research_detail_detect'](ui, detector=detector)
        ui.research_resume_interrupted_requirement.assert_called_once()
        ui.research_detail_quit.assert_called_once()
        ui.config.task_delay.assert_called_once_with(minute=30)


if __name__ == '__main__':
    unittest.main()
