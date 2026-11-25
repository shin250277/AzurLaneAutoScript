"""Extract only the public observed Korean cafe facility label."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((741, 496, 799, 518)).save(
            'assets/kr/island/KR_PRODUCTION_CAFE_VARIANT.png')
