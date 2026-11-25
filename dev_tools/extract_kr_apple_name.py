"""Extract only the observed public apple label for strict image matching."""
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
        if args.background_variant:
            source.convert('RGB').crop((304, 431, 450, 462)).save(
                'dev_tools/fixtures/kr_apple_name_background.png')
            with Image.open('assets/kr/island_item_name/2016_recipe_up_selected.png') as prior:
                prior.save('assets/kr/island_item_name/2016_recipe_up.png')
            raise SystemExit(0)
        source.convert('RGB').crop((304, 132, 450, 163)).save(
            'assets/kr/island_item_name/2016_recipe_up_selected.png')
