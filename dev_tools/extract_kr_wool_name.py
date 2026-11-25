"""Extract only the observed public wool label, never account/stock pixels."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--background-variant', action='store_true')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected observed 1280x720 recipe screen')
        area = (304, 133, 450, 164) if args.background_variant else (304, 137, 450, 160)
        suffix = 'background_selected' if args.background_variant else 'selected'
        source.convert('RGB').crop(area).save(
            'assets/kr/island_item_name/2605_recipe_{}.png'.format(suffix))
