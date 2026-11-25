"""Extract Korean event navigation from an observed 1280x720 frame."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    target = Path('assets/kr/shop/NAV_EVENT.png')
    if target.exists():
        raise SystemExit('Refusing to overwrite an existing asset')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 frame')
        area = (50, 537, 111, 558)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
