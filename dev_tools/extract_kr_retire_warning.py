"""Extract only the non-personal KR retirement warning label from an ALAS error frame."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 ALAS error frame')
        area = (441, 250, 835, 278)
        asset = Image.new('RGB', frame.size)
        asset.paste(frame.crop(area).convert('RGB'), area)
    output = Path(__file__).resolve().parents[1] / 'assets/kr/retire/KR_RETIRE_RARITY_WARNING.png'
    asset.save(str(output))
    print(output)


if __name__ == '__main__':
    main()
