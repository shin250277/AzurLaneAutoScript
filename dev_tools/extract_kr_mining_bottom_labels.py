"""Extract public mining names only from the observed bottom-list frame."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--top', action='store_true', help='Observed coal/copper top labels')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        rows = [(2700, 137), (2701, 286)] if args.top else [(2702, 94), (2703, 243), (2704, 392), (2705, 541)]
        for item, y in rows:
            source.convert('RGB').crop((304, y, 450, y + 23)).save(
                'assets/kr/island_item_name/{}_recipe_{}.png'.format(item, 'top' if args.top else 'bottom'))
