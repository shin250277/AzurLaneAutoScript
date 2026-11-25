"""Extract only the observed public sulfur name at the middle scroll offset."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected recipe frame size')
        source.convert('RGB').crop((304, 478, 450, 509)).save(
            'assets/kr/island_item_name/2704_recipe_middle_selected.png')
