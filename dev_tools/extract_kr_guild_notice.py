"""Extract the fixed guild-completion prefix, not account or mission details."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    target = Path('assets/kr/handler/KR_GUILD_NOTICE_CLOSE.png')
    if target.exists():
        raise SystemExit('Refusing to replace an existing verified asset')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 diagnostic frame')
        area = (470, 340, 621, 363)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
