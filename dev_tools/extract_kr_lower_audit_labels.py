"""Public name-only crops reviewed from the Nov 9 08:15 audit."""
import argparse
from pathlib import Path
from PIL import Image

LABELS = {
    '501_9101': [(2017, 394)],
    '602_9071': [(3104, 388)],
    '603_9081': [(3106, 238)],
    '604_9091': [(3033, 309), (3034, 458)],
    '703_9201': [(3049, 222)],
    '704_9203': [(3044, 152), (3046, 450)],
    '706_9207': [(3035, 155), (3037, 453)],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', action='store_true')
    args = parser.parse_args()
    for key, labels in LABELS.items():
        with Image.open('log/kr_island_recipe_audit_%s.png' % key) as source:
            if source.size != (1280, 720):
                raise ValueError('Unexpected frame size')
            for item, top in labels:
                target = ('assets/kr/island_item_name/%s_lower_audit_selected.png' % item
                          if args.reference else 'dev_tools/fixtures/kr_lower_audit_%s.png' % item)
                source.convert('RGB').crop((304, top, 450, top+31)).save(target)
