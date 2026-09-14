"""Extract the observed Korean acquisition label (not the share action)."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--queue', action='store_true')
    args = parser.parse_args()
    name = 'MEOWFFICER_TRAIN_FILL_QUEUE' if args.queue else 'MEOWFFICER_GET_CHECK'
    target = Path('assets/kr/meowfficer') / (name + '.png')
    if target.exists():
        raise SystemExit('Refusing to overwrite existing asset')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 frame')
        area = (780, 546, 859, 570) if args.queue else (30, 664, 83, 692)
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
