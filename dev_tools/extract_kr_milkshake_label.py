"""Name-only crop from reviewed Nov 9 cafe failure; no account pixels."""
import argparse
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', action='store_true')
    args = parser.parse_args()
    with Image.open('log/kr_island_recipe_audit_901_9041.png') as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        target = ('assets/kr/island_item_name/3010_cafe_selected.png' if args.reference
                  else 'dev_tools/fixtures/kr_milkshake_label.png')
        source.convert('RGB').crop((304, 330, 450, 361)).save(target)
