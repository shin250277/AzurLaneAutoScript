"""Extract observed island page titles, without account or inventory data."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--page', choices=('order', 'season'), required=True)
    args = parser.parse_args()
    target = Path('assets/kr/ui/ISLAND_%s_CHECK.png' % args.page.upper())
    if target.exists():
        raise SystemExit('Refusing to replace a verified asset')
    area = (125, 19, 220, 46)
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 ALAS diagnostic frame')
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
