"""Audit KR movable mappings, not game screenshots or task success."""
import ast
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from module.base.resource import Resource


def audit():
    root = Path('doc')
    with (root / 'KR_MOVABLE_ASSET_EVIDENCE.csv').open(encoding='utf8') as f:
        evidence = {(r['module'], r['name']): r['movable_scan'] for r in csv.DictReader(f)}
    counts = Counter()
    stages = defaultdict(set)
    for p in sorted(Path('campaign').rglob('*.py')):
        code = p.read_text(encoding='utf-8-sig')
        if 'MAP_SIREN_TEMPLATE' not in code:
            continue
        for stmt in ast.walk(ast.parse(code)):
            if not isinstance(stmt, ast.Assign) or not any(
                    isinstance(k, ast.Name) and k.id == 'MAP_SIREN_TEMPLATE' for k in stmt.targets):
                continue
            try:
                names = ast.literal_eval(stmt.value)
            except (ValueError, SyntaxError):
                continue
            if isinstance(names, (tuple,list)):
                for name in names:
                    stages['TEMPLATE_SIREN_'+str(name)].add(p.as_posix())
    with (root / 'KR_SPRITE_PARITY.csv').open('w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(('module', 'template', 'kr_source', 'byte_identical_regions', 'replay',
                         'explicit_siren_stage_count', 'example_explicit_stage'))
        for src in sorted(Path('module').rglob('assets.py')):
            for n in ast.parse(src.read_text(encoding='utf-8-sig')).body:
                if not isinstance(n, ast.Assign) or not isinstance(n.value, ast.Call):
                    continue
                if getattr(n.value.func, 'id', '') != 'Template':
                    continue
                mapping = ast.literal_eval(next(k.value for k in n.value.keywords if k.arg == 'file'))
                paths = {s: Path(Resource.parse_property(mapping, s)) for s in ('kr', 'cn', 'en', 'jp', 'tw')}
                digest = {s: hashlib.sha256(p.read_bytes()).digest() for s, p in paths.items()}
                same = [s for s in ('cn', 'en', 'jp', 'tw') if digest[s] == digest['kr']]
                name = n.targets[0].id
                result = evidence.pop((src.as_posix(), name))
                linked = sorted(stages[name])
                writer.writerow((src.as_posix(), name, paths['kr'].as_posix(), '|'.join(same), result,
                                 len(linked) if name.startswith('TEMPLATE_SIREN_') else '',
                                 next(iter(linked), '')))
                counts[result, len(same)] += 1
    if evidence:
        raise ValueError('Replay contains definitions absent from the current source')
    print(sorted(counts.items()))


if __name__ == '__main__':
    audit()
