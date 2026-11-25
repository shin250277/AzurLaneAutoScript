"""Second-pass search for region-dependent templates. No device or game input."""
import csv
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageSequence

from dev_tools.kr_movable_template_replay import images


def spots(frame, preview, sprite):
    h, w = sprite.shape[:2]
    small = cv2.resize(cv2.cvtColor(sprite, cv2.COLOR_RGB2GRAY),
                       (max(1, round(w/2)), max(1, round(h/2))), interpolation=cv2.INTER_AREA)
    if small.std() < 6:
        return False
    scores = cv2.matchTemplate(preview, small, cv2.TM_CCOEFF_NORMED)
    for _ in range(3):
        _, score, _, (x, y) = cv2.minMaxLoc(scores)
        if score < .62:
            break
        roi = frame[max(0, 2*y-5):2*y+h+6, max(0, 2*x-5):2*x+w+6]
        if roi.shape[0] >= h and roi.shape[1] >= w:
            _, fine, _, (u, v) = cv2.minMaxLoc(cv2.matchTemplate(roi, sprite, cv2.TM_CCOEFF_NORMED))
            if fine >= .94 and np.abs(roi[v:v+h, u:u+w].astype(np.int16)-sprite).mean() <= 14:
                return True
        scores[max(0,y-2):y+3, max(0,x-2):x+3] = -1
    return False


def run():
    root = Path('doc')
    with (root/'KR_SPRITE_PARITY.csv').open(encoding='utf8') as f:
        rows = [r for r in csv.DictReader(f) if r['replay'] == 'no_candidate'
                and r['byte_identical_regions'] != 'cn|en|jp|tw']
    variants = {}
    for r in rows:
        with Image.open(r['kr_source']) as im:
            variants[r['template']] = [np.array(i.convert('RGB')) for i in ImageSequence.Iterator(im)]
    dirs = [Path('log')/s for s in ('kr_capture_20261124', 'kr_inner_20261124',
            'kr_menu_capture_20261122', 'kr_submenu_20261123', 'kr_daily_replay_20261123',
            'kr_dorm_replay_20261123')]
    for d in Path('log/error').iterdir():
        record = d/'log.txt'
        if record.is_file():
            regions = re.findall(r'\[Server\]\s+(\w+)', record.read_text(encoding='utf8', errors='replace'))
            if regions and regions[-1] == 'kr':
                dirs.append(d)
    def frames():
        yield from images(dirs)
        for p in sorted(Path('log').glob('kr_*.png')):
            with Image.open(p) as im:
                if im.size == (1280, 720):
                    yield np.asarray(im.convert('RGB'))
    found = set()
    count = 0
    for frame in frames():
        count += 1
        thumb = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (640,360), interpolation=cv2.INTER_AREA)
        for name in variants.keys()-found:
            if any(spots(frame, thumb, p) for p in variants[name]):
                found.add(name)
    if not count:
        raise ValueError('No KR frames')
    with (root/'KR_REGIONAL_SPRITE_REPLAY.csv').open('w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(('template','regional_replay'))
        writer.writerows((r['template'], 'visual_candidate' if r['template'] in found else 'not_observed') for r in rows)
    print(count, 'frame visits;', len(found), 'new candidates of', len(rows))


if __name__ == '__main__':
    cv2.setNumThreads(1)
    run()
