"""Extract verified public Korean plate labels for disambiguating similar icons."""
from pathlib import Path
from PIL import Image
from dev_tools.check_kr_event_shop_frame import scan_frame
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--legacy', action='store_true')
args = parser.parse_args()
source = ('dev_tools/fixtures/kr_event_shop_middle.png' if args.legacy else
          'dev_tools/fixtures/kr_event_shop_plate_raster.png')
frame, grid = scan_frame(source)
folder = Path('assets/shop/event_kr_names')
folder.mkdir(exist_ok=True)
names = ('PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3')
buttons = grid.grids.buttons
if args.legacy:
    names = ('PlateGeneralT3', 'PlateGunT3', 'PlateTorpedoT3')
    buttons = buttons[2:]
for name, button in zip(names, buttons):
    path = folder / (name + ('__legacy' if args.legacy else '') + '.png')
    if path.exists():
        raise SystemExit('Refusing to overwrite template')
    x, y = button.area[:2]
    Image.fromarray(frame[y+72:y+100, x-44:x+108]).save(str(path))
if not args.legacy:
    path = folder / 'PlateGeneralT3.png'
    if path.exists():
        raise SystemExit('Refusing to overwrite template')
    with Image.open('log/kr_event_shop_scan_05.png') as image:
        image.crop((899, 602, 1049, 631)).save(str(path))
