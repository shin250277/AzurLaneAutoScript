"""Read-only localization coverage, not a claim of live feature correctness.

No account configuration, screenshots, device or network is accessed. Distinguish
upstream-shared assets from region-dependent fallbacks instead of counting all
non-Korean paths as either broken or verified.
"""
import ast
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ('cn', 'en', 'jp', 'tw')


def classify(fields):
    files = fields.get('file')
    if not isinstance(files, dict):
        return 'shared-literal'
    if not files.get('kr'):
        return 'missing-kr-mapping'
    if '/kr/' in files['kr'].replace('\\', '/'):
        return 'kr-specific'
    # Shared image alone is insufficient: crop and color may be regional.
    for value in fields.values():
        if not isinstance(value, dict):
            continue
        values = [value.get(region) for region in REGIONS + ('kr',)]
        if any(v is None for v in values) or any(v != values[0] for v in values):
            return 'regional-fallback-review'
    return 'upstream-shared'


def assets(root=ROOT):
    rows = []
    for path in sorted((root / 'module').rglob('assets.py')):
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in tree.body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if not isinstance(call.func, ast.Name) or call.func.id not in ('Button', 'Template'):
                continue
            fields = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
            rows.append({'module': path.parent.name, 'name': node.targets[0].id,
                         'classification': classify(fields)})
    return rows


def menu_coverage(root=ROOT):
    menu = json.loads((root / 'module/config/argument/menu.json').read_text(encoding='utf-8'))
    names = sorted({name for group in menu.values() for name in group.get('tasks', [])})
    matrix = (root / 'doc/KR_FEATURE_MATRIX.md').read_text(encoding='utf-8')
    return {'menu_count': len(names),
            'not_documented': [name for name in names if '| `%s` |' % name not in matrix]}


def report():
    rows = assets()
    counts = Counter(row['classification'] for row in rows)
    review = Counter(row['module'] for row in rows
                     if row['classification'] == 'regional-fallback-review')
    return {'generated_assets': len(rows), 'classification': dict(sorted(counts.items())),
            'regional_review_by_module': dict(sorted(review.items())),
            'missing_kr_mappings': [r for r in rows if r['classification'] == 'missing-kr-mapping'],
            'menu': menu_coverage(),
            'meaning': 'Regional fallback is a review candidate, not a proven failure. '
                       'Shared and KR-specific paths do not prove live matching.'}


if __name__ == '__main__':
    print(json.dumps(report(), ensure_ascii=False, indent=2))
