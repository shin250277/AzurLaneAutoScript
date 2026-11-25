"""Extract public mining names only from the observed bottom-list frame."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--top', action='store_true', help='Observed coal/copper top labels')
    parser.add_argument('--iron-offset', action='store_true', help='Observed iron name at detected y242')
    parser.add_argument('--sulfur-context', action='store_true', help='Public sulfur name with four-pixel vertical context')
    parser.add_argument('--iron-up-context', action='store_true', help='Observed iron name on upward scroll')
    parser.add_argument('--sulfur-bright', action='store_true', help='Public bright sulfur label at y463')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        if args.sulfur_bright:
            source.convert('RGB').crop((304, 463, 450, 494)).save(
                'dev_tools/fixtures/kr_sulfur_bright_name.png')
            raise SystemExit(0)
        if args.iron_up_context:
            source.convert('RGB').crop((304, 500, 450, 531)).save(
                'assets/kr/island_item_name/2703_recipe_up_selected.png')
            raise SystemExit(0)
        if args.sulfur_context:
            source.convert('RGB').crop((304, 387, 450, 418)).save(
                'dev_tools/fixtures/kr_sulfur_name_context.png')
            raise SystemExit(0)
        if args.iron_offset:
            source.convert('RGB').crop((304, 242, 450, 265)).save(
                'assets/kr/island_item_name/2703_recipe_offset_selected.png')
            raise SystemExit(0)
        rows = [(2700, 137), (2701, 286)] if args.top else [(2702, 94), (2703, 243), (2704, 392), (2705, 541)]
        for item, y in rows:
            source.convert('RGB').crop((304, y, 450, y + 23)).save(
                'assets/kr/island_item_name/{}_recipe_{}.png'.format(item, 'top' if args.top else 'bottom'))
