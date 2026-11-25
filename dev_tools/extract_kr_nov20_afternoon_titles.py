"""Extract reviewed public titles only from hash-pinned local failures."""
import hashlib
from pathlib import Path
from PIL import Image

if __name__ == '__main__':
    for filename, digest, entries in (
            ('601_9062', '0a1ef307b18bb44f84a79d305c97c6b82b113988f72d6b579a2ab6e807b173cf',
             [(3015, 168), (3114, 317)]),
            ('706_9207', '6c09c2193d4d2d9d97d4d74859ec5e5931536bcb16059d820d244bb411634bc3',
             [(3035, 193)])):
        path = Path('log/kr_island_recipe_audit_%s.png' % filename)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed frame requires review')
        with Image.open(str(path)) as frame:
            for item, y in entries:
                frame.convert('RGB').crop((304,y,450,y+31)).save(
                    'assets/kr/island_item_name/%s_nov20_afternoon_selected.png' % item)
    path = Path('log/kr_island_dispatch_name_9091.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '06be3a201fd57f432b63377633a91a55c24a45090b73ad4443191fe9489b0b5a':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304,295,450,326)).save(
            'assets/kr/island_item_name/3115_nov20_afternoon_selected.png')
