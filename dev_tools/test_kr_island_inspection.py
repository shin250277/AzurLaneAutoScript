"""Read-only island inspection must never invoke submission or production."""
import subprocess
import sys
import unittest
import json
import ast
from pathlib import Path


class IslandInspectionTest(unittest.TestCase):
    def test_order_inspection_only_selects_left_side_orders(self):
        code = '''
from unittest.mock import Mock
from module.island.inspect import IslandInspect
ui = Mock()
ui.regular_orders = [Mock(button=(10, 200, 100, 300)), Mock(button=(900, 600, 1200, 680))]
ui.urgent_orders = []
ui.season_orders = []
IslandInspect.inspect_order_pages(ui)
assert ui.click_order.call_count == 1
assert ui.scan_current_order_requirements.call_count == 1
ui.submit_order.assert_not_called()
ui.reject_order.assert_not_called()
ui.run_any_order.assert_not_called()
ui.config.cross_set.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_task_inspection_is_bounded_and_never_changes_targets(self):
        code = '''
from unittest.mock import Mock, patch
from module.island.inspect import IslandInspect
ui = Mock()
ui.get_task_codename.return_value = []
ui.season_task_grid.buttons = []
with patch('module.island.inspect.ISLAND_SEASON_TASK_SCROLL') as scroll:
    scroll.at_bottom.return_value = False
    IslandInspect.inspect_task_pages(ui)
    assert ui.device.image_save.call_count == 12
    assert scroll.next_page.call_count == 11
    ui.config.cross_set.assert_not_called()
    ui.receive_all_reward.assert_not_called()
    ui.run_any_order.assert_not_called()
ui.reset_mock()
with patch('module.island.inspect.ISLAND_SEASON_TASK_SCROLL') as scroll:
    scroll.at_bottom.return_value = True
    IslandInspect.inspect_task_pages(ui)
    assert ui.device.image_save.call_count == 1
    scroll.next_page.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_pages_use_observed_korean_titles(self):
        tree = ast.parse(Path('module/ui/assets.py').read_text(encoding='utf-8'))
        for name in ('ISLAND_ORDER_CHECK', 'ISLAND_SEASON_CHECK'):
            node = next(n for n in tree.body if isinstance(n, ast.Assign)
                        and n.targets[0].id == name)
            values = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
            self.assertEqual(values['file']['kr'], './assets/kr/ui/%s.png' % name)
            self.assertEqual(values['area']['kr'], (125, 19, 220, 46))

    def test_entrypoint_initializes_server_before_import(self):
        tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                      and n.name == 'island_inspect')
        setter = next(n for n in ast.walk(method) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name) and n.func.id == 'set_server')
        imported = next(n for n in ast.walk(method) if isinstance(n, ast.ImportFrom)
                        and n.module == 'module.island.inspect')
        self.assertLess(setter.lineno, imported.lineno)
        self.assertEqual(setter.args[0].attr, 'Emulator_PackageName')

    def test_tool_menu_and_translations_are_connected(self):
        from module.submodule.utils import get_available_func
        self.assertIn('IslandInspect', get_available_func())
        menu = json.loads(Path('module/config/argument/menu.json').read_text(encoding='utf-8'))
        self.assertIn('IslandInspect', menu['Tool']['tasks'])
        args = json.loads(Path('module/config/argument/args.json').read_text(encoding='utf-8'))
        self.assertEqual(args['IslandInspect'], {})
        for path in Path('module/config/i18n').glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            self.assertIn('IslandInspect', data['Task'], str(path))

    def test_inspection_only_navigates_and_saves_frames(self):
        code = '''
from unittest.mock import Mock, call
from module.island.inspect import IslandInspect
from module.ui.page import page_island_order, page_island_season
ui = Mock()
ui.config.SERVER = 'kr'
IslandInspect.run(ui)
assert ui.ui_ensure.call_args_list == [call(page_island_order), call(page_island_season)]
ui.island_season_bottom_navbar_ensure.assert_called_once_with(left=3)
ui.inspect_task_pages.assert_called_once_with()
assert ui.device.screenshot.call_count == 3
assert ui.device.image_save.call_count == 4
ui.device.click.assert_not_called()
ui.config.cross_set.assert_not_called()
ui.config.task_delay.assert_not_called()
ui.run_any_order.assert_not_called()
ui.receive_all_reward.assert_not_called()
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
