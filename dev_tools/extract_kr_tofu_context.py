"""Retain only the public long tofu recipe label for substring regression."""
import argparse
from PIL import Image

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('frame')
    with Image.open(p.parse_args().frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        label = source.convert('RGB').crop((304, 285, 450, 316))
        label.save('dev_tools/fixtures/kr_long_tofu_context.png')
        label.save('assets/kr/island_item_name/3012_recipe_long_selected.png')
