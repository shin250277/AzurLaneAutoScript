"""Extract reviewed public title-only references from local audit frames."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    for filename, digest, item, y in (
            ('kr_island_recipe_audit_402_9021.png',
             'd869af7b64f868f9650c2412fa39ba8238df15e879ea1f504b954a34e215aba5', 2802, 389),
            ('kr_island_recipe_audit_501_9101.png',
             'ba702cf70e7385db2794a11787d61927ec753e5b97b3d6eb4be12d7827bd370c', 4049, 282),
            ('kr_island_recipe_audit_601_9061.png',
             '0583ceafaa2e0550f9c848d759b9ae243ca677a1f032a454440414042c167d89', 4052, 282),
            ('kr_island_recipe_audit_706_9207.png',
             'db7ad6376207202379aaf7fbeeb5c44781cd44005623bd4cee27b1b2975e65fb', 3039, 239)):
        path = Path('log') / filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed frame requires visual review')
        with Image.open(str(path)) as frame:
            frame.convert('RGB').crop((304, y, 450, y + 31)).save(
                'assets/kr/island_item_name/%s_nov20_followup.png' % item)
