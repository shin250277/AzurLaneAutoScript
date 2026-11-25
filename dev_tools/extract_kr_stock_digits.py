"""Extract a numeral-only OCR regression sample; no account/stock labels."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        frame.convert('RGB').crop((393, 208, 456, 230)).save(
            'dev_tools/fixtures/kr_stock_repeated_digits.png')
