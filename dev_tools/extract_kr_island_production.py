"""Extract only observed production labels from an ALAS diagnostic frame."""
import argparse
from pathlib import Path
from PIL import Image

TOP = {
    'FIELD': (201, 83, 299, 103), 'RANCH': (741, 83, 855, 103),
    'FISHERY': (201, 267, 299, 286), 'MINE': (741, 267, 815, 286),
    'WOOD': (201, 450, 315, 469), 'ORCHARD': (741, 450, 870, 469),
    'NURSERY': (201, 633, 299, 652), 'KOI': (741, 633, 855, 652),
}
MIDDLE = {
    'BEAR': (201, 368, 279, 390), 'EATERY': (741, 368, 837, 390),
    'GRILL': (201, 552, 298, 574), 'LUMBER': (741, 552, 820, 574),
}
BOTTOM = {
    'MACHINERY': (201, 317, 281, 338), 'ELECTRONIC': (741, 317, 858, 338),
    'CRAFTS': (201, 501, 299, 522), 'CAFE': (741, 501, 799, 522),
}
BUSINESS_TOP = {
    'KOI': (221, 97, 375, 124), 'BEAR': (221, 274, 325, 301),
    'EATERY': (221, 451, 348, 478), 'GRILL': (221, 628, 348, 655),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--receive', action='store_true')
    parser.add_argument('--middle', action='store_true')
    parser.add_argument('--bottom', action='store_true')
    parser.add_argument('--business-top', action='store_true')
    parser.add_argument('--restaurant-empty', action='store_true')
    parser.add_argument('--business-bottom', action='store_true')
    args = parser.parse_args()
    prefix = 'BUSINESS' if args.business_top or args.business_bottom else 'PRODUCTION'
    areas = BUSINESS_TOP if args.business_top else BOTTOM if args.bottom else MIDDLE if args.middle else TOP
    if args.business_bottom:
        areas = {'CAFE': (221, 531, 297, 557)}
    targets = ([(Path('assets/kr/island/ISLAND_PRODUCTION_RECEIVE.png'), (589, 547, 629, 570))]
               if args.receive else
               [(Path('assets/kr/island/TEMPLATE_ISLAND_' + prefix + '_' + name + '.png'), area)
                for name, area in areas.items()])
    if args.restaurant_empty:
        targets = [(Path('assets/kr/island_handler/ISLAND_RESTAURANT_CHECK.png'), (124, 20, 214, 44)),
                   (Path('assets/kr/island_handler/KR_RESTAURANT_EMPTY.png'), (721, 297, 910, 315))]
    if any(path.exists() for path, area in targets):
        raise SystemExit('Refusing to overwrite existing labels')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 ALAS frame')
        for path, area in targets:
            if args.receive or (args.restaurant_empty and path.name == 'ISLAND_RESTAURANT_CHECK.png'):
                canvas = Image.new('RGB', frame.size)
                canvas.paste(frame.crop(area).convert('RGB'), area)
                canvas.save(str(path))
            else:
                frame.crop(area).convert('RGB').save(str(path))


if __name__ == '__main__':
    main()
