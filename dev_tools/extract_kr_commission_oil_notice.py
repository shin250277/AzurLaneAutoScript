"""Extract only the observed oil-cost notice for vision matching."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 KR commission frame')
        canvas = Image.new('RGB', frame.size)
        area = (422, 329, 856, 360)
        canvas.paste(frame.crop(area).convert('RGB'), area)
    target = Path(__file__).resolve().parents[1] / 'assets/kr/commission/KR_OIL_NOTICE.png'
    canvas.save(str(target))


if __name__ == '__main__':
    main()
