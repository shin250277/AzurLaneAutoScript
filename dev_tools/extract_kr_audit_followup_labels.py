"""Public labels from the 07:49 audit, not the earlier overwritten frames."""
import argparse
from pathlib import Path
from PIL import Image

LABELS = {
    '201_9211': [(5103, 192)],
    '502_9111': [(2015, 239), (2004, 388), (2007, 537)],
}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder')
    folder = Path(p.parse_args().folder)
    for key, labels in LABELS.items():
        with Image.open(str(folder / ('kr_island_recipe_audit_%s.png' % key))) as source:
            if source.size != (1280, 720):
                raise ValueError('Unexpected frame size')
            for item, top in labels:
                source.convert('RGB').crop((304, top, 450, top + 31)).save(
                    'assets/kr/island_item_name/%s_recipe_followup_selected.png' % item)
