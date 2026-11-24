"""Make fixed-position, UI-only furniture shop references from a KR frame."""
from pathlib import Path
import sys
from PIL import Image


def extract(path):
    with Image.open(path) as im:
        if im.size != (1280, 720):
            raise ValueError('Expected a 1280x720 furniture shop')
        for name, box in [('TITLE', (91, 19, 208, 63)), ('ENTER', (1097, 452, 1169, 488))]:
            dst = Path('assets/kr/dorm/KR_THEME_SHOP_' + name + '.png')
            if dst.exists():
                raise FileExistsError(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            masked = Image.new('RGB', im.size)
            masked.paste(im.crop(box).convert('RGB'), box)
            masked.save(dst)


if __name__ == '__main__':
    extract(sys.argv[1])
