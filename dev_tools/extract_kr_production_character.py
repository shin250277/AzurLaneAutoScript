"""Extract public KR character-placement text, excluding facility/account data."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        area = (612, 328, 695, 351)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.convert('RGB').crop(area), area[:2])
        canvas.save('assets/kr/island/KR_PRODUCTION_SELECT_CHARACTER.png')
