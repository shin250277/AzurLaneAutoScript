"""Extract only the two public UI labels; never export a full account frame."""
import argparse
from pathlib import Path
from PIL import Image


def extract(source):
    root = Path('assets/kr/ui')
    targets = [('KR_CARD_CAPTION', (1057, 672, 1240, 694)),
               ('KR_CARD_ZOOM', (30, 462, 56, 496))]
    if any((root / (name + '.png')).exists() for name, _ in targets):
        raise FileExistsError('Already extracted')
    with Image.open(source) as image:
        if image.size != (1280, 720):
            raise ValueError('Expected 1280x720 KR registered-ship screen')
        for name, box in targets:
            masked = Image.new('RGB', image.size)
            masked.paste(image.crop(box).convert('RGB'), box)
            masked.save(root / (name + '.png'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('frame', type=Path)
    extract(ap.parse_args().frame)
