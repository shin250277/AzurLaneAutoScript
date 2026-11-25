"""Join local visual scans to the KR asset inventory without publishing frame paths."""
import argparse
import ast
import csv
from collections import Counter, defaultdict
from pathlib import Path

from dev_tools.kr_compatibility_audit import ROOT, classify


def direct_roles(known):
    """Index direct, unambiguous source uses; never infer pass from a name."""
    result = defaultdict(set)
    for path in (ROOT / 'module').rglob('*.py'):
        if path.name == 'assets.py':
            continue
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        scope = defaultdict(set)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            src = node.module.replace('.', '/') + '.py'
            if src not in known:
                continue
            for alias in node.names:
                if alias.name == '*':
                    for name in known[src]:
                        scope[name].add((src, name))
                elif alias.name in known[src]:
                    scope[alias.asname or alias.name].add((src, alias.name))
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Name) or len(scope.get(node.id, ())) != 1:
                continue
            parent = parents.get(node)
            if isinstance(parent, ast.Attribute):
                op = parent.attr
            elif isinstance(parent, ast.Call):
                op = getattr(parent.func, 'attr', None) or getattr(parent.func, 'id', '')
            else:
                op = ''
            if op in ('click', 'multi_click', 'long_click'):
                role = 'click'
            elif op in ('appear', 'appear_then_click', 'match', 'match_luma', 'match_template_color',
                        'match_binary', 'appear_on', 'match_result', 'match_multi'):
                role = 'visual'
            elif op in ('image_color_count', 'get_color', 'color'):
                role = 'color'
            elif op in ('Ocr', 'Digit', 'DigitCounter', 'Duration', 'Counter'):
                role = 'ocr'
            elif op in ('area', 'button', 'crop', 'load_offset', 'wait_until_stable'):
                role = 'geometry'
            else:
                role = 'indirect'
            result[next(iter(scope[node.id]))].add(role)
    return result


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
    known = defaultdict(set)
    for src, name, _, _, _ in rows:
        known[src].add(name)
    roles = direct_roles(known)
    with output.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(('module', 'name', 'type', 'kr_mapping', 'fixed_position_scan', 'source_uses'))
        for row in rows:
            writer.writerow(row + ('|'.join(sorted(roles[row[:2]])) or 'not_resolved',))
    print(len(rows), 'definitions;', dict(Counter(r[-1] for r in rows)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('inputs', type=Path, nargs='+')
    args = parser.parse_args()
    generate(args.inputs, args.output)
