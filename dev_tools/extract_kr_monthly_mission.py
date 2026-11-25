"""Extract only the observed Korean Arbiter title from an ALAS mission frame."""
import argparse
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    target = Path('assets/kr/os_handler/MISSION_MONTHLY_BOSS.png')
    if target.exists():
        raise SystemExit('Asset already exists; inspect before replacing it')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected an ALAS 1280x720 frame with Arbiter as the first mission')
        area = (566, 186, 710, 207)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
    canvas.save(str(target))


if __name__ == '__main__':
    main()
