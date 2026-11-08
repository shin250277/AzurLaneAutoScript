"""Public text only, reviewed 08:30-08:33 Nov 9 translucent sky background."""
import argparse
from PIL import Image

LABELS = {
    '401_9011': [(2703, 273)],
    '601_9061': [(4009, 132)],
    '602_9071': [(3103, 429)],
    '603_9081': [(3023, 132)],
    '604_9091': [(3030, 281)],
    '703_9201': [(3049, 281)],
    '704_9203': [(3042, 132)],
    '706_9207': [(3035, 145)],
    '901_9041': [(3007, 280)],
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
                target = ('assets/kr/island_item_name/%s_sky_selected.png' % item
                          if args.reference else 'dev_tools/fixtures/kr_sky_%s.png' % item)
                source.convert('RGB').crop((304, top, 450, top+31)).save(target)
