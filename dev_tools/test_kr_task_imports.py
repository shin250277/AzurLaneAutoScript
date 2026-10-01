"""Load actual gameplay entry-point imports without constructing a device."""
import subprocess
import sys
import unittest


class KoreanTaskImportTest(unittest.TestCase):
    def test_gameplay_entry_point_imports(self):
        code = '''
import ast
import importlib
import json
import inflection
from pathlib import Path
from unittest.mock import patch
import module.config.server as server
server.server = 'kr'
tree = ast.parse(Path('alas.py').read_text(encoding='utf-8'))
script = next(node for node in tree.body
              if isinstance(node, ast.ClassDef) and node.name == 'AzurLaneAutoScript')
checked = set()
menu = json.loads(Path('module/config/argument/menu.json').read_text(encoding='utf-8'))
commands = {inflection.underscore(task)
            for group in menu.values() if group['page'] == 'setting'
            for task in group['tasks']}
with patch('socket.socket.connect', side_effect=AssertionError('No network in import smoke test')):
    for method in script.body:
        if not isinstance(method, ast.FunctionDef):
            continue
        # Derive scheduler tasks from the menu, excluding standalone tools.
        if method.name not in commands:
            continue
        for node in ast.walk(method):
            if isinstance(node, ast.ImportFrom) and node.module.startswith('module.'):
                module = importlib.import_module(node.module)
                for name in node.names:
                    if name.name != '*':
                        assert hasattr(module, name.name), (node.module, name.name)
                checked.add(node.module)
assert len(checked) >= 25, checked
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], timeout=60,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    unittest.main()
