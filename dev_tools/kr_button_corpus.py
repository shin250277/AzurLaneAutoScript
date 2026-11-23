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


def scan(directories, report):
    frames = []
    for directory in directories:
        for p in sorted(directory.glob('*.png')):
            with Image.open(str(p)) as im:
                if im.size == (1280, 720):
                    frames.append((p.stem, np.array(im.convert('RGB'))))
    if not frames:
        raise ValueError('No 1280x720 frames')
    rows = []
    for src, name, fields in targets():
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
        rows.append((src, name, status, evidence))
    with report.open('w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(('module', 'button', 'status', 'frame'))
        writer.writerows(rows)
    print(len(frames), 'frames;', len(rows), 'definitions;', dict(Counter(r[2] for r in rows)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('directories', type=Path, nargs='+')
    args = parser.parse_args()
    scan(args.directories, args.report)
