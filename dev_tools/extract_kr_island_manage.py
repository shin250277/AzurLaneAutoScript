"""Extract the observed Korean island-management title, without account data."""
import argparse
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    target = Path('assets/kr/ui/ISLAND_MANAGE_CHECK.png')
    if target.exists():
        raise SystemExit('Asset already exists; inspect before replacing it')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 island-management frame')
        area = (125, 21, 214, 45)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
    canvas.save(str(target))


if __name__ == '__main__':
    main()
