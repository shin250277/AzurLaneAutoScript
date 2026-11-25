"""Restore full-frame coordinates for previously cropped KR button assets."""
from pathlib import Path
import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shooting-frame', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'assets/kr/minigame'
    for name, area in [('START', (250, 418, 515, 498)),
                       ('END', (945, 557, 1083, 615))]:
        path = root / ('NEW_YEAR_CHALLENGE_' + name + '.png')
        with Image.open(str(path)) as source:
            if source.size == (1280, 720):
                continue
            if source.size != (area[2] - area[0], area[3] - area[1]):
                raise ValueError('Unexpected asset dimensions: ' + str(path))
            canvas = Image.new('RGB', (1280, 720))
            canvas.paste(source.convert('RGB'), area)
        canvas.save(str(path))
    if args.shooting_frame:
        with Image.open(str(args.shooting_frame)) as frame:
            if frame.size != (1280, 720):
                raise ValueError('Expected a 1280x720 ALAS error frame')
            area = (109, 19, 270, 61)
            canvas = Image.new('RGB', frame.size)
            canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(root / 'KR_SHOOTING_GAME_CHECK.png'))


if __name__ == '__main__':
    main()
