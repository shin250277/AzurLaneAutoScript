"""Extract only the observed public wool label, never account/stock pixels."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected observed 1280x720 recipe screen')
        source.convert('RGB').crop((304, 137, 450, 160)).save(
            'assets/kr/island_item_name/2605_recipe_selected.png')
