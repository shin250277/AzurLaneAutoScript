"""Reviewed public title strips only; changed local frames require review."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    for filename, digest, item, y in (
            ('704_9203', '9f7291a888a6313bf8f919747d94a63b6bfdaeb462dc5a10b12ca9e1a5948514', 3046, 444),
            ('706_9207', '0d15be2f59fe40ef7940b8ebb31a03148c000cb4c8b0455d8ee085cb6545ccad', 3036, 296)):
        path = Path('log/kr_island_recipe_audit_%s.png' % filename)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed frame requires visual review')
        with Image.open(str(path)) as frame:
            frame.convert('RGB').crop((304, y, 450, y + 31)).save(
                'assets/kr/island_item_name/%s_nov20_followup.png' % item)
    path = Path('log/kr_island_dispatch_name_9103.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '7c8f486c0c51227675d07342adef6135d330a84f2cbbeaed9f847c2607eaeb5b':
        raise ValueError('Changed frame requires visual review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 288, 450, 319)).save(
            'assets/kr/island_item_name/2017_nov20_followup.png')
    path = Path('log/kr_island_dispatch_name_9071.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != 'a5389e9cdab382c1270170626788c5a21285b4dacd978cba91bb572960fc74f1':
        raise ValueError('Changed frame requires visual review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 223, 450, 254)).save(
            'assets/kr/island_item_name/3021_nov20_followup.png')
