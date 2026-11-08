"""Extract the public selected banana label, without inventory or account UI."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((304, 121, 450, 152)).save(
            'assets/kr/island_item_name/2018_recipe_selected.png')
