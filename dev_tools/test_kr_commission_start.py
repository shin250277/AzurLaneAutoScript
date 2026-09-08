"""A KR start click is not evidence that a commission started."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class CommissionStartTest(unittest.TestCase):
    def test_start_click_waits_for_confirmation(self):
        path = Path(__file__).resolve().parents[1] / 'module/commission/commission.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == '_commission_start_click')
        tree.body = [method]
        scope = dict(logger=Mock(), Timer=Mock(return_value=Mock()),
                     COMMISSION_ADVICE='advice', COMMISSION_START='start')
        exec(compile(tree, str(path), 'exec'), scope)
        handler = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                                  interval_clear=Mock(), interval_reset=Mock(),
                                  info_bar_count=Mock(side_effect=[0, 1]),
                                  appear=Mock(return_value=True), device=Mock())
        self.assertTrue(scope['_commission_start_click'](handler, Mock()))
        handler.device.click.assert_called_once_with('start')
        handler.device.screenshot.assert_called_once()
        self.assertEqual(handler.info_bar_count.call_count, 2)


if __name__ == '__main__':
    unittest.main()
