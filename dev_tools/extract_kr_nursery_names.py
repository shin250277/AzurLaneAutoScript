"""Keep only four observed public nursery labels, no stocks or account UI."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        for item, top, suffix in ((2010, 133, 'selected'), (2011, 282, 'middle'),
                                  (2012, 431, 'middle'), (2014, 580, 'bottom')):
            frame.convert('RGB').crop((304, top, 450, top + 31)).save(
                'assets/kr/island_item_name/{}_recipe_{}.png'.format(item, suffix))
