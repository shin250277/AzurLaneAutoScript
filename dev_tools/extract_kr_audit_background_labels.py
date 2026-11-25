"""Reviewed 07:56-07:59 public labels; no stock, characters or account pixels."""
import argparse
from pathlib import Path
from PIL import Image

LABELS = {
    '601_9061': [(3012, 278)],
    '602_9071': [(3019, 437)],
    '603_9081': [(3025, 291), (3026, 440)],
    '604_9091': [(3030, 282)],
    '703_9201': [(3048, 133)],
    '704_9203': [(3044, 134)],
    '706_9207': [(3035, 125), (3037, 423)],
    '901_9041': [(3059, 133)],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder')
    parser.add_argument('--reference', action='store_true')
    args = parser.parse_args()
    for key, labels in LABELS.items():
        with Image.open(str(Path(args.folder) / ('kr_island_recipe_audit_%s.png' % key))) as source:
            if source.size != (1280, 720):
                raise ValueError('Unexpected frame size')
            for item, top in labels:
                target = ('assets/kr/island_item_name/%s_background_selected.png' % item if args.reference
                          else 'dev_tools/fixtures/kr_background_%s.png' % item)
                source.convert('RGB').crop((304, top, 450, top+31)).save(target)
