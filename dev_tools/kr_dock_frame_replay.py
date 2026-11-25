"""Detect actual dock pages in local KR diagnostics; do not export account panels."""
import argparse
import re
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
import module.config.server as server


def sources():
    for folder in Path('log/error').iterdir():
        record = folder/'log.txt'
        if not record.is_file():
            continue
        regions = re.findall(r'\[Server\]\s+(\w+)', record.read_text(encoding='utf8', errors='replace'))
        if regions and regions[-1] == 'kr':
            yield from folder.glob('*.png')
    yield from Path('log').glob('kr_*.png')
    for folder in ['kr_menu_capture_20261122','kr_submenu_20261123','kr_inner_20261124']:
        yield from (Path('log')/folder).glob('*')


def run(verbose=False):
    server.set_server('kr')
    from module.retire.assets import DOCK_CHECK
    from module.retire.scanner import FleetScanner, StatusScanner
    fleet, status = FleetScanner(), StatusScanner()
    total, ids, states = 0, Counter(), Counter()
    for p in sources():
        if p.suffix.lower() not in ('.jpg','.png'):
            continue
        with Image.open(str(p)) as im:
            if im.size != (1280,720):
                continue
            frame = np.array(im.convert('RGB'))
        if DOCK_CHECK.match_template_color(frame, offset=(3,3), similarity=.91):
            total += 1
            a, b = fleet._scan(frame), status._scan(frame)
            ids.update(a)
            states.update(b)
            if verbose:
                print(p, a, sorted(set(b)))
    print('Dock-header matches (including overlays), inferred fleets/statuses:',total,ids,states)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose',action='store_true')
    run(parser.parse_args().verbose)
