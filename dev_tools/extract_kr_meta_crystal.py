"""Extract public crystal-label and comment-button UI only; no account data."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame dimensions')
        canvas = Image.new('RGB', source.size)
        for area in ((1145, 400, 1270, 438), (42, 465, 83, 510)):
            canvas.paste(source.convert('RGB').crop(area), area[:2])
        canvas.save('assets/kr/meta_reward/KR_CRYSTAL_CARD.png')
