"""Extract the observed public persimmon label without stock/account pixels."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--background-variant', action='store_true')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected recipe frame size')
        suffix = 'background_selected' if args.background_variant else 'top_selected'
        source.convert('RGB').crop((304, 282, 450, 313)).save(
            'assets/kr/island_item_name/4007_recipe_{}.png'.format(suffix))
