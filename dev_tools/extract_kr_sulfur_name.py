"""Extract only the public sulfur name from the observed lower mine list."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((304, 387, 450, 418)).save(
            'assets/kr/island_item_name/2704_recipe_lower_selected.png')
