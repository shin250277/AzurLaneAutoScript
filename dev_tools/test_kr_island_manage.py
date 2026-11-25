"""The white island-management screen is not the white main navigation bar."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


class KoreanIslandManageTest(unittest.TestCase):
    def test_real_ui_module_can_execute_guard_without_device(self):
        from module.ui.ui import UI
        from module.ui.page import page_main
        ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                             appear=lambda *args, **kwargs: False)
        self.assertFalse(UI.ui_page_appear(ui, page_main))

    def test_manage_title_uses_local_asset(self):
        tree = ast.parse(Path('module/ui/assets.py').read_text(encoding='utf-8'))
        call = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'ISLAND_MANAGE_CHECK')
        values = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
        self.assertEqual(values['file']['kr'], './assets/kr/ui/ISLAND_MANAGE_CHECK.png')

    def test_main_detection_excludes_manage_but_keeps_actual_main(self):
        tree = ast.parse(Path('module/ui/ui.py').read_text(encoding='utf-8'))
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == 'ui_page_appear')
        tree.body = [fn]
        scope = {n.id: n.id for n in ast.walk(fn) if isinstance(n, ast.Name)
                 and n.id.isupper()}
        scope.update({n.id: SimpleNamespace(check_button=n.id) for n in ast.walk(fn)
                      if isinstance(n, ast.Name) and n.id.startswith('page_')})
        exec(compile(tree, 'module/ui/ui.py', 'exec'), scope)
        for foreground in (None, 'page_island_manage', 'ISLAND_CHECK'):
            with self.subTest(foreground=foreground):
                ui = SimpleNamespace(config=SimpleNamespace(SERVER='kr'),
                    appear=lambda button, **kwargs: button == 'MAIN_GOTO_DOCK_WHITE'
                    or (foreground is not None and button == foreground))
                self.assertEqual(scope['ui_page_appear'](ui, scope['page_main']), foreground is None)


if __name__ == '__main__':
    unittest.main()
