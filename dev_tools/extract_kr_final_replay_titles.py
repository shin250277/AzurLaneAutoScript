"""Extract only visually reviewed public names from pinned local KR frames."""
from hashlib import sha256
from pathlib import Path
from PIL import Image


def main():
    sources = [
        ('kr_island_dispatch_name_9012.png',
         'c4be3385f12ea8200f1c670c8de5ad345d4200f5acefe6355cc5ad676a8d4c91',
         [(2704, (304, 421, 450, 452))]),
        ('kr_island_recipe_audit_604_9091.png',
         '50f9aeccf51b53860c6338be280e5c13bad76ed53f9426852691fcfbc41ba495',
         [(3034, (304, 114, 450, 145)), (3115, (304, 263, 450, 294))]),
    ]
    for filename, digest, labels in sources:
        path = Path('log') / filename
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed source requires visual review: ' + filename)
        with Image.open(str(path)) as frame:
            for item, box in labels:
                frame.convert('RGB').crop(box).save(
                    'assets/kr/island_item_name/%s_nov20_replay_selected.png' % item)


if __name__ == '__main__':
    main()
