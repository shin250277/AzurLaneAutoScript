import ast
import unittest
from pathlib import Path
from unittest.mock import Mock


class EventShopScanTest(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path('module/shop_event/scan.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        module = ast.Module(body=[cls])
        namespace = {'EventShop': object, 'RequestHumanTakeover': RuntimeError, 'logger': Mock()}
        exec(compile(module, '<scan>', 'exec'), namespace)
        self.scan = namespace['EventShopScan']()

    def test_both_purchase_entrypoints_refuse(self):
        for method in (self.scan.event_shop_buy_item, self.scan.event_shop_buy_item_execute):
            with self.assertRaisesRegex(RuntimeError, 'Purchases are disabled'):
                method(Mock(), amount=1)

    def test_scan_reads_points_and_items_only(self):
        self.scan.event_shop_load_ensure = Mock()
        self.scan.get_current_pts = Mock()
        self.scan.scan_all = Mock(return_value=[Mock()])
        self.assertTrue(self.scan._run())
        self.scan.event_shop_load_ensure.assert_called_once_with()
        self.scan.get_current_pts.assert_called_once_with()
        self.scan.scan_all.assert_called_once_with()

    def test_inspection_does_not_reschedule_regular_shop(self):
        self.scan.config = Mock()
        self.scan.schedule_next_run()
        self.scan.config.task_delay.assert_not_called()

    def test_tool_initializes_kr_before_import_and_captures_before_run(self):
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'event_shop_scan')
        setter = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name) and n.func.id == 'set_server')
        imported = next(n for n in ast.walk(method) if isinstance(n, ast.ImportFrom)
                        and n.module == 'module.shop_event.scan')
        self.assertEqual(setter.args[0].attr, 'Emulator_PackageName')
        self.assertLess(setter.lineno, imported.lineno)
        calls = [n.value.func.attr for n in method.body if isinstance(n, ast.Expr)
                 and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)]
        self.assertLess(calls.index('screenshot'), calls.index('run'))

    def test_navigation_uses_localized_active_category_not_legacy_color(self):
        tree = ast.parse(Path('module/shop_event/shop_event.py').read_text(encoding='utf-8'))
        run = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'run')
        checks = [n for n in ast.walk(run) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Attribute) and n.func.attr == 'ui_page_appear']
        self.assertTrue(any(isinstance(n.args[0], ast.Name) and n.args[0].id == 'page_munitions'
                            for n in checks))
        kr = next(n for n in ast.walk(run) if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                  and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                          and c.func.attr == 'click' and c.args
                          and isinstance(c.args[0], ast.Name) and c.args[0].id == 'KR_MUNITIONS_CHECK'
                          for stmt in n.body for c in ast.walk(stmt)))
        self.assertNotIn('SHOP_GOTO_MUNITIONS', [n.id for stmt in kr.body for n in ast.walk(stmt)
                                              if isinstance(n, ast.Name)])
