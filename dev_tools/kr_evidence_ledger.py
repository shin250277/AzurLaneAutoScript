"""Join local visual scans to the KR asset inventory without publishing frame paths."""
import argparse
import ast
import csv
from collections import Counter, defaultdict
from pathlib import Path

from dev_tools.kr_compatibility_audit import ROOT, classify


def generate(inputs, output):
    statuses = defaultdict(set)
    for report in inputs:
        with report.open(encoding='utf-8') as stream:
            for row in csv.DictReader(stream):
                statuses[row['module'], row['button']].add(row['status'])
    # Offline scan outcomes are not positive/negative functional tests.
    priority = ('visual_candidate', 'nearby_visual_candidate', 'no_visual_evidence',
                'no_fixed_match', 'not_scanned')
    rows = []
    for path in sorted((ROOT / 'module').rglob('assets.py')):
        src = path.relative_to(ROOT).as_posix()
        for node in ast.parse(path.read_text(encoding='utf-8-sig')).body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            kind = getattr(node.value.func, 'id', '')
            if kind not in ('Button', 'Template'):
                continue
            name = node.targets[0].id
            fields = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
            evidence = next((s for s in priority if s in statuses[src, name]), 'outside_fixed_scan')
            rows.append((src, name, kind, classify(fields), evidence))
    with output.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(('module', 'name', 'type', 'kr_mapping', 'fixed_position_scan'))
        writer.writerows(rows)
    print(len(rows), 'definitions;', dict(Counter(r[-1] for r in rows)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('inputs', type=Path, nargs='+')
    args = parser.parse_args()
    generate(args.inputs, args.output)
