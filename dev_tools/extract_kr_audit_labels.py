"""Extract reviewed public label-only crops from the Nov 9 facility audit.

Never retains stock, character, inventory, or account pixels. The two long
restaurant labels are the observed clipped rendering, not synthesized text;
all variants are exact-only references.
"""
import argparse
from pathlib import Path
from PIL import Image


LABELS = {
    '501_9101': [(2018, 475)],
    '502_9111': [(2010, 133)],
    '601_9061': [(4009, 133), (4010, 282), (3011, 431)],
    '602_9071': [(4013, 133), (4014, 282), (3017, 431), (3018, 580)],
    '603_9081': [(3023, 133), (3009, 282), (3024, 431), (3025, 580)],
    '604_9091': [(3029, 133), (3030, 282), (3032, 431)],
    '703_9201': [(3049, 224), (3050, 373), (3051, 522)],
    '704_9203': [(3042, 133), (3043, 282), (3044, 431), (3045, 580)],
    '705_9205': [(3053, 133), (3054, 282), (3055, 431), (3056, 580)],
    '706_9207': [(4011, 133), (4012, 282), (3035, 431), (3036, 580)],
    '901_9041': [(3006, 182), (3007, 331), (3008, 480)],
}


def extract(folder):
    for facility, labels in LABELS.items():
        with Image.open(str(Path(folder) / ('kr_island_recipe_audit_%s.png' % facility))) as source:
            if source.size != (1280, 720):
                raise ValueError('Unexpected observed frame size')
            for item, top in labels:
                source.convert('RGB').crop((304, top, 450, top + 31)).save(
                    'assets/kr/island_item_name/%s_recipe_audit_selected.png' % item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder')
    extract(parser.parse_args().folder)
