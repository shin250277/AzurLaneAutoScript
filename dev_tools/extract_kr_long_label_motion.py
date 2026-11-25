"""Public long-label crop from the reviewed 08:19 fractional-scroll rendering."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    with Image.open(parser.parse_args().frame) as source:
        if source.size != (1280,720):
            raise ValueError('Unexpected frame size')
        source.convert('RGB').crop((304,296,450,327)).save('dev_tools/fixtures/kr_long_label_motion.png')
