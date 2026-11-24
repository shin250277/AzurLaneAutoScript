"""Inventory fixed-position visual evidence, not clicks or functional test results."""
import argparse
import ast
import csv
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from module.base.resource import Resource


def targets():
    for src in sorted(Path('module').rglob('assets.py')):
        for stmt in ast.parse(src.read_text(encoding='utf-8-sig')).body:
            if not isinstance(stmt, ast.Assign) or not isinstance(stmt.value, ast.Call):
                continue
            call = stmt.value
            if getattr(call.func, 'id', None) != 'Button':
                continue
            fields = {kw.arg: Resource.parse_property(ast.literal_eval(kw.value), 'kr')
                      for kw in call.keywords if kw.arg in ('file', 'area')}
            yield src.as_posix(), stmt.targets[0].id, fields


def scan_batch(files, nearby=False, resolved=()):
    frames = []
    for p in files:
        with Image.open(str(p)) as im:
            if im.size == (1280, 720):
                frames.append((str(p), np.array(im.convert('RGB'))))
    if not frames:
        return 0, []
    cv2.setNumThreads(1)
    grays = [cv2.cvtColor(im, cv2.COLOR_RGB2GRAY) for _, im in frames] if nearby else []
    rows = []
    for src, name, fields in targets():
        if (src, name) in resolved:
            continue
        path = fields.get('file')
        area = fields.get('area')
        status, evidence = 'not_scanned', ''
        if path and area and Path(path).suffix.lower() == '.png' and Path(path).is_file():
            x, y, r, b = area
            with Image.open(path) as im:
                if im.size == (1280, 720) and 0 <= x < r <= 1280 and 0 <= y < b <= 720:
                    patch = np.asarray(im.convert('RGB').crop(area))
                else:
                    patch = None
            if patch is not None and min(patch.shape[:2]) >= 4 and patch.std(axis=(0, 1)).max() >= 12:
                status = 'no_fixed_match'
                stride = max(1, min(b-y, r-x)//12)
                sample = patch[::stride, ::stride].astype(np.int16)
                for key, frame in frames:
                    region = frame[y:b, x:r]
                    if np.abs(region[::stride, ::stride] - sample).mean() > 17:
                        continue
                    if cv2.matchTemplate(region, patch, cv2.TM_CCOEFF_NORMED)[0, 0] >= .94:
                        if np.abs(region.astype(np.int16)-patch).mean() <= 14:
                            status, evidence = 'visual_candidate', key
                            break
                if nearby and status == 'no_fixed_match':
                    template = cv2.cvtColor(patch, cv2.COLOR_RGB2GRAY)
                    left, top = max(0, x-20), max(0, y-20)
                    if template.std() >= 10:
                        for (key, frame), gray in zip(frames, grays):
                            search = gray[top:b+20, left:r+20]
                            _, sim, _, (px, py) = cv2.minMaxLoc(cv2.matchTemplate(
                                search, template, cv2.TM_CCOEFF_NORMED))
                            if sim < .94:
                                continue
                            reg = frame[top+py:top+py+b-y, left+px:left+px+r-x]
                            if (np.abs(reg.astype(np.int16)-patch).mean() <= 14
                                    and cv2.matchTemplate(reg, patch, cv2.TM_CCOEFF_NORMED)[0,0] >= .94):
                                status, evidence = 'nearby_visual_candidate', key
                                break
                    if status == 'no_fixed_match':
                        status = 'no_visual_evidence'
        rows.append((src, name, status, evidence))
    return len(frames), rows


def scan(directories, report, nearby=False, recursive=False):
    files = sorted({p for d in directories for p in (d.rglob('*') if recursive else d.iterdir())
                    if p.suffix.lower() in ('.jpg', '.jpeg', '.png') and p.is_file()})
    evidence, resolved, count = {}, set(), 0
    for start in range(0, len(files), 32):
        size, rows = scan_batch(files[start:start+32], nearby, resolved)
        count += size
        for row in rows:
            key = row[:2]
            evidence[key] = row
            if row[2] in ('visual_candidate', 'nearby_visual_candidate', 'not_scanned'):
                resolved.add(key)
    if not count:
        raise ValueError('No 1280x720 frames')
    rows = [evidence[key] for key in sorted(evidence)]
    with report.open('w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(('module', 'button', 'status', 'frame'))
        writer.writerows(rows)
    print(count, 'frames;', len(rows), 'definitions;', dict(Counter(r[2] for r in rows)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('directories', type=Path, nargs='+')
    parser.add_argument('--nearby', action='store_true', help='also search a 20-pixel margin')
    parser.add_argument('--recursive', action='store_true', help='include nested local capture directories')
    args = parser.parse_args()
    scan(args.directories, args.report, args.nearby, args.recursive)
