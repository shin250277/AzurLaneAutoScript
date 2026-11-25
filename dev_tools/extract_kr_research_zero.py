"""Extract the observed zero-progress label, excluding account information."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('screenshot')
    args = parser.parse_args()
    with Image.open(args.screenshot) as image:
        if image.size != (1280, 720):
            raise ValueError('Expected 1280x720')
        image.convert('RGB').crop((1052, 529, 1105, 550)).save(
            'assets/kr/research/REQUIREMENT_ZERO_15.png')
