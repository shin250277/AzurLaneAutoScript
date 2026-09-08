"""Restore coordinates of known cropped KR buttons, preserving their pixels."""
from pathlib import Path
from PIL import Image


def main():
    root = Path(__file__).resolve().parents[1] / 'assets/kr'
    entries = [
        ('commission/COMMISSION_ADVICE.png', (870, 326, 997, 389)),
        ('commission/COMMISSION_START.png', (1028, 326, 1157, 389)),
        ('coalition/COALITION_REWARD_CONFIRM.png', (1090, 648, 1180, 688)),
    ]
    for relative, area in entries:
        path = root / relative
        with Image.open(str(path)) as source:
            if source.size == (1280, 720):
                continue
            if source.size != (area[2] - area[0], area[3] - area[1]):
                raise ValueError('Unexpected image dimensions: ' + str(path))
            canvas = Image.new('RGB', (1280, 720))
            canvas.paste(source.convert('RGB'), area)
        canvas.save(str(path))


if __name__ == '__main__':
    main()
