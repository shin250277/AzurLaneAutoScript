"""Extract only the observed oil-cost notice for vision matching."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--maxed', action='store_true')
    parser.add_argument('--five', action='store_true')
    args = parser.parse_args()
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 KR commission frame')
        canvas = Image.new('RGB', frame.size)
        area = (359, 310, 663, 337) if args.maxed else (422, 329, 856, 360)
        canvas.paste(frame.crop(area).convert('RGB'), area)
    filename = 'KR_OIL_MAXED.png' if args.maxed else 'KR_OIL_NOTICE.png'
    if args.five:
        if args.maxed:
            raise ValueError('Choose one notice')
        filename = 'KR_OIL_NOTICE_5.png'
    target = Path(__file__).resolve().parents[1] / 'assets/kr/commission' / filename
    if target.exists():
        raise SystemExit('Refusing to replace an existing template')
    canvas.save(str(target))


if __name__ == '__main__':
    main()
