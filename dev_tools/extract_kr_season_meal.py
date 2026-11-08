"""Extract only the publicly visible task title, excluding progress/account data."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--reference', action='store_true')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        title = source.convert('RGB').crop((466, 355, 707, 385))
        title.save('assets/kr/island_task_name/80001416_selected.png' if args.reference
                   else 'dev_tools/fixtures/kr_season_meal.png')
