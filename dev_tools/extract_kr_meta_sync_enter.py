"""Extract only the public Korean META sync label from a diagnostic frame."""
import argparse
from pathlib import Path
from PIL import Image


AREA = (856, 349, 952, 373)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    target = Path('assets/kr/meta_reward/SYNC_ENTER.png')
    if target.exists():
        raise SystemExit('Refusing to overwrite existing template')
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 game frame')
        result = Image.new('RGB', source.size)
        result.paste(source.crop(AREA).convert('RGB'), AREA)
        result.save(str(target))


if __name__ == '__main__':
    main()
