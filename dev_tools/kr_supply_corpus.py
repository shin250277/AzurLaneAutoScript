"""Locate KR pack-shop candidates locally. Positive page detection is not proof of a free pack."""
import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
from module.config import server


def run(root):
    server.set_server('kr')
    from module.freebies.supply_pack import SupplyPack_250814, FREE_SUPPLY_PACK
    from module.ui.page import page_supply_pack
    obj = object.__new__(SupplyPack_250814)
    obj.config = SimpleNamespace(SERVER='kr')
    obj.device = SimpleNamespace(stuck_record_add=lambda button: None)
    seen = set()
    for p in sorted(root.rglob('*')):
        if p.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        with Image.open(str(p)) as im:
            if im.size != (1280, 720):
                continue
            obj.device.image = np.asarray(im.convert('RGB'))
        if not obj.match_template_color(page_supply_pack.check_button, offset=(20, 20)):
            continue
        signature = hashlib.sha256(obj.device.image[165:644, 195:1010].tobytes()).digest()
        if signature in seen:
            continue
        seen.add(signature)
        print('CANDIDATE', int(obj.appear(FREE_SUPPLY_PACK, offset=(200, 20))), p, flush=True)
    print('Unique pack-shop product layouts:', len(seen))


if __name__ == '__main__':
    run(Path(sys.argv[1]))
