"""One-time mechanical resolution of generated files during the 2026-09 upstream merge.

Only run in the expected merge. Python/control-flow conflicts are resolved manually.
"""
import json
import re
import subprocess
from pathlib import Path


def stage(number, path):
    return subprocess.check_output(['git', 'show', ':{}:{}'.format(number, path)]).decode('utf-8')


def merge_json(base, ours, theirs):
    if ours == base:
        return theirs
    if theirs == base or ours == theirs:
        return ours
    if all(isinstance(value, dict) for value in (base, ours, theirs)):
        result = dict(theirs)
        for key, value in ours.items():
            if key not in theirs:
                if key not in base or value != base[key]:
                    result[key] = value
            elif key in base:
                result[key] = merge_json(base[key], value, theirs[key])
            else:
                result[key] = theirs[key]
        return result
    # Generated options will be rebuilt from the merged source configuration.
    return theirs


if __name__ == '__main__':
    expected = '46fe341db463aa82a3ee4dbdd3899042561dd7ec'
    actual = subprocess.check_output(['git', 'rev-parse', 'MERGE_HEAD']).decode().strip()
    if actual != expected:
        raise SystemExit('Not the expected upstream merge')
    files = ['module/config/argument/args.json'] + [
        'module/config/i18n/{}.json'.format(lang)
        for lang in ['en-US', 'ja-JP', 'zh-CN', 'zh-TW']]
    for name in files:
        merged = merge_json(*(json.loads(stage(n, name)) for n in (1, 2, 3)))
        Path(name).write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Event names/schedules from upstream; KR display names live in KR_EVENT_NAMES.
    # Assets below are regenerated using the merged PNGs and KR fallback rules.
    for name in ['campaign/Readme.md', 'module/handler/assets.py',
                 'module/map/assets.py', 'module/shop/assets.py']:
        path = Path(name)
        content = path.read_text(encoding='utf-8')
        content = re.sub(r'^<<<<<<< .*?\n.*?^=======\n(.*?)^>>>>>>> .*?\n',
                         lambda match: match.group(1), content, flags=re.M | re.S)
        path.write_text(content, encoding='utf-8')
