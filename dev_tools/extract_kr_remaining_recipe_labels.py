"""Public text-only crops reviewed from Nov 9 08:41-43 audit frames."""
import argparse
from PIL import Image

LABELS = [('601_9061',3114,240), ('602_9071',3103,414),
          ('603_9081',3025,296), ('706_9207',3036,285), ('901_9041',3007,282),
          ('704_9203',3044,379)]

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--reference', action='store_true')
    args = p.parse_args()
    for key, item, top in LABELS:
        if args.reference and item in (3025, 3036):
            # Existing references suffice with bounded lighting agreement.
            continue
        with Image.open('log/kr_island_recipe_audit_%s.png' % key) as source:
            if source.size != (1280,720):
                raise ValueError('Unexpected frame size')
            target = ('assets/kr/island_item_name/%s_remaining_selected.png' % item if args.reference
                      else 'dev_tools/fixtures/kr_remaining_%s.png' % item)
            source.convert('RGB').crop((304,top,450,top+31)).save(target)
