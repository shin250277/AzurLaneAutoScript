"""Keep only the observed public mango recipe name, without account UI."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((304, 297, 450, 328)).save(
            'assets/kr/island_item_name/2019_recipe_middle.png')
