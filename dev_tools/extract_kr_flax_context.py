"""Extract public flax text only for background-robust recognition regression."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((304, 133, 450, 164)).save(
            'dev_tools/fixtures/kr_flax_background.png')
