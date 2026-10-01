"""Extract public localized island controls from diagnostic frames."""
from pathlib import Path
import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--label', choices=('order-submit', 'business-cancel', 'restaurant-recommend', 'restaurant-start'), default='order-submit')
    args = parser.parse_args()
    filename, area = {
        'order-submit': ('island/KR_IRON_ORDER_SUBMIT.png', (1115, 639, 1169, 665)),
        'business-cancel': ('island/ISLAND_BUSINESS_EVENT_POPUP_CANCEL.png', (479, 632, 552, 658)),
        'restaurant-recommend': ('island_handler/ISLAND_RESTAURANT_RECOMMEND.png', (284, 612, 383, 640)),
        'restaurant-start': ('island_handler/ISLAND_RESTAURANT_START.png', (713, 612, 810, 640)),
    }[args.label]
    target = Path('assets/kr') / filename
    if target.exists():
        raise SystemExit('Refusing to replace an existing template')
    with Image.open(args.frame) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720')
        result = Image.new('RGB', frame.size)
        result.paste(frame.crop(area).convert('RGB'), area)
        result.save(str(target))


if __name__ == '__main__':
    main()
