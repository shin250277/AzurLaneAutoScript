"""Mask account/background data from the eight observed shop scan pages."""
from pathlib import Path
from PIL import Image

target = Path('dev_tools/fixtures/kr_shop_oct02_sequence')
if target.exists():
    raise SystemExit('Refusing to overwrite sequence')
target.mkdir()
for number in range(1, 9):
    with Image.open('log/kr_event_shop_scan_%02d.png' % number) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected game frame')
        output = Image.new('RGB', source.size)
        area = (221, 194, 1049, 632)
        output.paste(source.crop(area), area[:2])
        output.save(str(target / ('%02d.png' % number)))
