"""Extract only the observed public lemon label, never account/stock pixels."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--background-variant', action='store_true')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected observed 1280x720 recipe screen')
        if args.background_variant:
            source.convert('RGB').crop((304, 239, 450, 270)).save(
                'dev_tools/fixtures/kr_lemon_name_background.png')
            # The prior independently observed label supplies the regular
            # shape template; the new failure remains separate test evidence.
            with Image.open('dev_tools/fixtures/kr_lemon_name_context.png') as prior:
                prior.save('assets/kr/island_item_name/2020_recipe_bottom.png')
            raise SystemExit(0)
        source.convert('RGB').crop((304, 239, 450, 270)).save(
            'dev_tools/fixtures/kr_lemon_name_context.png')
        source.convert('RGB').crop((304, 239, 450, 270)).save(
            'assets/kr/island_item_name/2020_recipe_bottom_selected.png')
