"""Read-only feature inventory. Never import runners, devices or account config."""
import ast
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def inventory():
    menu = json.loads((ROOT / 'module/config/argument/menu.json').read_text(encoding='utf-8'))
    source = yaml.safe_load((ROOT / 'module/config/argument/task.yaml').read_text(encoding='utf-8'))
    tree = ast.parse((ROOT / 'alas.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AzurLaneAutoScript')
    handlers = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    rows = []
    for group in dict.fromkeys(list(menu) + list(source)):
        visible = menu.get(group, {}).get('tasks', [])
        defined = source.get(group, {}).get('tasks', {})
        for task in dict.fromkeys(list(visible) + list(defined)):
            handler = re.sub(r'(?<!^)(?=[A-Z])', '_', task).lower()
            rows.append(dict(group=group, task=task, arguments=defined.get(task, []),
                             in_menu=task in visible, in_source=task in defined,
                             handler=handler, handler_exists=handler in handlers))
    return rows


if __name__ == '__main__':
    print(json.dumps(inventory(), ensure_ascii=False, indent=2))
