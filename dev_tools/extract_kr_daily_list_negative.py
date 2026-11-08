"""Keep only public info icon and selector-lookalike art for offline tests."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected daily frame size')
        source.convert('RGB').crop((795, 265, 1005, 381)).save(
            'dev_tools/fixtures/kr_daily_list_selector_negative.png')
        source.convert('RGB').crop((0, 626, 97, 720)).save(
            'dev_tools/fixtures/kr_daily_list_info.png')
