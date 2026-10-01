"""Extract only the public localized submit label from a diagnostic frame."""
from pathlib import Path
import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    target = Path('assets/kr/island/KR_IRON_ORDER_SUBMIT.png')
    if target.exists():
        raise SystemExit('Refusing to replace an existing template')
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720')
        area = (1115, 639, 1169, 665)
        result = Image.new('RGB', frame.size)
        result.paste(frame.crop(area).convert('RGB'), area)
        result.save(str(target))


if __name__ == '__main__':
    main()
