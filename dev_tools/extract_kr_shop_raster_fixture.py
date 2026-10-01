"""Preserve only public shop rows from the observed rasterization failures."""
from pathlib import Path
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('frame', type=int)
parser.add_argument('label', choices=('design_raster', 'design_counter', 'plate_raster', 'blueprint_amount'))
args = parser.parse_args()
for number, label in ((args.frame, args.label),):
    target = Path('dev_tools/fixtures/kr_event_shop_%s.png' % label)
    if target.exists():
        raise SystemExit('Refusing to overwrite fixture')
    with Image.open('log/kr_event_shop_scan_%02d.png' % number) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720')
        output = Image.new('RGB', source.size)
        area = (221, 194, 1049, 632)
        output.paste(source.crop(area), area[:2])
        output.save(str(target))
