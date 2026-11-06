"""Extract public mining names only from the observed bottom-list frame."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        for item, y in [(2702, 94), (2703, 243), (2704, 392), (2705, 541)]:
            source.convert('RGB').crop((304, y, 450, y + 23)).save(
                'assets/kr/island_item_name/{}_recipe_bottom.png'.format(item))
