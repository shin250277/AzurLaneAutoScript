"""Extract the observed public 152mm MK.XXVI design icon; never buy items."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--template', action='store_true')
    parser.add_argument('--shifted', action='store_true')
    parser.add_argument('--augment', action='store_true')
    args = parser.parse_args()
    suffix = '_shifted' if args.shifted else ''
    target = Path(('assets/shop/event_kr/Design152mmMKXXVIT3' + ('__shifted' if args.shifted else '') + '.png')
                  if args.template else 'dev_tools/fixtures/kr_event_shop_' +
                  ('augment' if args.augment else 'design' + suffix) + '.png')
    if target.exists():
        raise SystemExit('Refusing to overwrite existing image')
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 game frame')
        if args.template:
            from dev_tools.check_kr_event_shop_frame import scan_frame
            frame, grid = scan_frame(args.frame)
            grid.predict(frame, save_unknown=False)
            matches = [item for item in grid.items if item.price == 135 and item.total_count == 15]
            if len(matches) != 1:
                raise ValueError('Expected exactly one observed design item')
            result = Image.fromarray(matches[0].image)
        else:
            result = Image.new('RGB', source.size)
            area = (221, 194, 1049, 632)
            result.paste(source.crop(area).convert('RGB'), area[:2])
        result.save(str(target))


if __name__ == '__main__':
    main()
