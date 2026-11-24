"""Offline KR sprite search. A match is an image candidate, not a task pass."""
import argparse
import ast
import csv
import hashlib
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageSequence

from module.base.resource import Resource


def definitions():
    for src in sorted(Path('module').rglob('assets.py')):
        for node in ast.parse(src.read_text(encoding='utf-8-sig')).body:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            if getattr(node.value.func, 'id', '') != 'Template':
                continue
            for kw in node.value.keywords:
                if kw.arg == 'file':
                    yield src.as_posix(), node.targets[0].id, Path(Resource.parse_property(
                        ast.literal_eval(kw.value), 'kr'))


def images(dirs):
    seen = set()
    for directory in dirs:
        for path in sorted(directory.glob('*')):
            if path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
                continue
            digest = hashlib.sha256(path.read_bytes()).digest()
            if digest in seen:
                continue
            seen.add(digest)
            with Image.open(path) as im:
                if im.size == (1280, 720):
                    yield np.array(im.convert('RGB'))


def search(frame, preview, sprite):
    h, w = sprite.shape[:2]
    thumb = cv2.resize(cv2.cvtColor(sprite, cv2.COLOR_RGB2GRAY),
                       (max(1, round(w/4)), max(1, round(h/4))), interpolation=cv2.INTER_AREA)
    if thumb.std() < 6:
        return False
    _, score, _, (x, y) = cv2.minMaxLoc(cv2.matchTemplate(preview, thumb, cv2.TM_CCOEFF_NORMED))
    if score < .65:
        return False
    left, top = max(0, x*4-7), max(0, y*4-7)
    roi = frame[top:y*4+h+8, left:x*4+w+8]
    if roi.shape[0] < h or roi.shape[1] < w:
        return False
    _, score, _, (x, y) = cv2.minMaxLoc(cv2.matchTemplate(roi, sprite, cv2.TM_CCOEFF_NORMED))
    return score >= .94 and np.abs(roi[y:y+h, x:x+w].astype(np.int16)-sprite).mean() <= 14


def run(output, dirs):
    rows, eligible, found = list(definitions()), {}, set()
    for _, _, path in rows:
        if path not in eligible and path.suffix.lower() in ('.png', '.gif'):
            with Image.open(path) as im:
                if 4 <= min(im.size) and im.width <= 1280 and im.height <= 720:
                    variants = [np.array(part.convert('RGB')) for part in ImageSequence.Iterator(im)]
                    variants = [part for part in variants if part.std(axis=(0, 1)).max() >= 12]
                    if variants:
                        eligible[path] = variants
    count = 0
    for frame in images(dirs):
        count += 1
        preview = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (320, 180),
                             interpolation=cv2.INTER_AREA)
        for key in eligible.keys()-found:
            if any(search(frame, preview, part) for part in eligible[key]):
                found.add(key)
    if not count:
        raise ValueError('No KR frames')
    with output.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(('module', 'name', 'movable_scan'))
        for module, name, path in rows:
            writer.writerow((module, name, 'visual_candidate' if path in found else
                             'no_candidate' if path in eligible else 'not_scanned'))
    print(count, 'frames;', len(rows), 'definitions;', len(eligible), 'eligible unique files;',
          len(found), 'unique candidates')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('dirs', type=Path, nargs='+')
    args = parser.parse_args()
    cv2.setNumThreads(1)
    run(args.output, args.dirs)
