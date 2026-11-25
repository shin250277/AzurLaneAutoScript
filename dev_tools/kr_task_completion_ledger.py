"""Local, read-only log audit. Export only menu names, counts and dates."""
import csv
import re
from collections import defaultdict
from pathlib import Path

from dev_tools.kr_live_asset_evidence import SERVER, TASK


def completed(lines):
    server = active = None
    valid = False
    for line in lines:
        region = SERVER.search(line)
        if region:
            server = region.group(1)
            if server != 'kr':
                valid = False
        marker = TASK.search(line)
        if marker:
            action, name = marker.groups()
            if action == 'Start':
                active, valid = name, server == 'kr'
            else:
                if active == name and valid:
                    yield name
                active, valid = None, False
        elif any(x in line for x in ('| ERROR', '| CRITICAL', 'Traceback (most recent call last)')):
            valid = False


def main():
    matrix = Path('doc/KR_FEATURE_MATRIX.md').read_text(encoding='utf8')
    menus = re.findall(r'^\| `(\w+)` \|', matrix.split('## 메뉴 외 실행 진입점', 1)[0], re.M)
    if len(menus) != len(set(menus)) or not menus:
        raise ValueError('Missing or duplicated menu row')
    records = defaultdict(list)
    for p in sorted(Path('log').glob('????-??-??_alas.txt')):
        with p.open(encoding='utf8', errors='replace') as src:
            for name in completed(src):
                records[name].append(p.name[:10])
    with Path('doc/KR_TASK_END_EVIDENCE.csv').open('w', newline='', encoding='utf8') as dst:
        writer = csv.writer(dst, lineterminator='\n')
        writer.writerow(('menu', 'completed_task_pairs', 'last_observed'))
        for name in menus:
            runs = records[name]
            writer.writerow((name, len(runs), runs[-1] if runs else ''))
    print(len(menus), 'menu rows;', sum(bool(records[n]) for n in menus), 'with a clean KR end')


if __name__ == '__main__':
    main()
