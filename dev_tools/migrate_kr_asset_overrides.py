"""Preserve verified KR metadata as generator input, not edits to generated assets."""
import ast
import json
import subprocess
from pathlib import Path


def definitions(text):
    result = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id in ('Button', 'Template'):
                result[node.targets[0].id] = (node.value.func.id,
                    {k.arg: ast.literal_eval(k.value) for k in node.value.keywords})
    return result


if __name__ == '__main__':
    target = Path('dev_tools/kr_asset_overrides.json')
    if target.exists():
        raise SystemExit('Overrides already exist')
    result = {}
    for path in sorted(Path('module').glob('*/assets.py')):
        try:
            old = definitions(subprocess.check_output([
                'git', 'show', '2b73346f5:' + path.as_posix()], stderr=subprocess.DEVNULL).decode('utf-8'))
        except subprocess.CalledProcessError:
            continue
        new = definitions(path.read_text(encoding='utf-8'))
        items = {}
        for name, (kind, values) in old.items():
            if name not in new:
                if any(isinstance(v, dict) and 'kr' in v for v in values.values()):
                    items[name] = dict(kind=kind, definition=values)
                continue
            changes = {key: value['kr'] for key, value in values.items()
                       if isinstance(value, dict) and 'kr' in value
                       and value['kr'] != new[name][1].get(key, {}).get('kr')}
            if changes:
                items[name] = dict(kr=changes)
        if items:
            result[path.parent.name] = items
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Preserved overrides:', sum(len(v) for v in result.values()))
