"""Extract only the observed disabled Korean research confirmation label."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    target = Path('assets/kr/research/RESEARCH_UNAVAILABLE.png')
    if target.exists():
        raise SystemExit('Refusing to replace an existing verified asset')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 ALAS diagnostic frame')
        area = (430, 563, 582, 600)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
