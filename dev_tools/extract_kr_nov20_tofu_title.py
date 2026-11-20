"""Extract only the reviewed public recipe title, never account details."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_601_9061.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '8bda079343090d9afc88d834c345f1605babaf6f0a8a09ff8cb860c142941019':
        raise ValueError('Changed frame requires visual review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 267, 450, 298)).save(
            'assets/kr/island_item_name/3012_nov20_followup.png')
    path = Path('log/kr_island_recipe_audit_602_9072.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '3292384775e2ab2f917fee6b6a277bd7aeb5528ff1c3df57371b821470a725ae':
        raise ValueError('Changed frame requires visual review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 552, 450, 583)).save(
            'assets/kr/island_item_name/3105_nov20_followup.png')
    for filename, digest, item, y in (
            ('703_9201', '8714734fc956e4b67e3de93a22a52c67a0398553a30f027870354fa04fc9275f', 3048, 132),
            ('704_9203', '7457a71035644da57551350f0c132bcde0c5dbfc5d897cbbb432dfa0feedc28d', 3043, 252),
            ('706_9207', 'a509d5e7cc530cd2fad13cd0e84f1d0dbba974159f30c12d0bc88b7dc910ef63', 4056, 281)):
        path = Path('log/kr_island_recipe_audit_%s.png' % filename)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed frame requires visual review')
        with Image.open(str(path)) as frame:
            frame.convert('RGB').crop((304, y, 450, y + 31)).save(
                'assets/kr/island_item_name/%s_nov20_followup%s.png' % (item, '_selected' if item == 4056 else ''))
    path = Path('log/kr_island_dispatch_name_9081.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != 'd72811205548ee11bf1cf16b1e35b25ec5287b7ed509420db698dce1f44422e7':
        raise ValueError('Changed frame requires visual review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 329, 450, 360)).save(
            'assets/kr/island_item_name/3028_nov20_followup_selected.png')
