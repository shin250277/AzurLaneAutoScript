"""Read-only KR generated asset integrity audit; no device or account imports."""
import ast
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def regional(value):
    return value.get('kr') if isinstance(value, dict) else value


def inspect_asset(identity, kind, fields):
    filename = fields.get('file')
    row = dict(id=identity, kind=kind, file=filename, errors=[],
               source='kr-path' if filename and '/kr/' in filename else 'foreign-or-shared',
               evidence='static-only')
    if not filename or not (ROOT / filename).is_file():
        row['errors'].append('missing file')
        return row
    try:
        with Image.open(str(ROOT / filename)) as im:
            row['size'] = im.size
            row['frames'] = getattr(im, 'n_frames', 1)
            for index in range(row['frames']):
                im.seek(index)
                im.load()
            if not im.width or not im.height:
                row['errors'].append('empty image')
    except (OSError, ValueError) as exc:
        row['errors'].append('image decode: ' + type(exc).__name__)
    for key in ('area', 'button'):
        rect = fields.get(key)
        if rect is not None:
            if (not isinstance(rect, (tuple, list)) or len(rect) != 4
                    or not all(isinstance(v, (int, float)) for v in rect)
                    or not (0 <= rect[0] < rect[2] <= 1280
                            and 0 <= rect[1] < rect[3] <= 720)):
                row['errors'].append('invalid ' + key)
            elif key == 'area' and 'size' in row and (
                    rect[2] > row['size'][0] or rect[3] > row['size'][1]):
                row['errors'].append('area exceeds image')
    return row


def inventory():
    rows = []
    for path in sorted((ROOT / 'module').rglob('assets.py')):
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in tree.body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if not isinstance(call.func, ast.Name) or call.func.id not in ('Button', 'Template'):
                continue
            fields = {kw.arg: regional(ast.literal_eval(kw.value)) for kw in call.keywords}
            identity = path.relative_to(ROOT).as_posix() + ':' + node.targets[0].id
            rows.append(inspect_asset(identity, call.func.id, fields))
    return rows


if __name__ == '__main__':
    rows = inventory()
    print(json.dumps(dict(total=len(rows),
                         kr_paths=sum(r['source'] == 'kr-path' for r in rows),
                         errors=[r for r in rows if r['errors']],
                         limitation='Static integrity only, not observed KR matching'),
                     ensure_ascii=False, indent=2))
