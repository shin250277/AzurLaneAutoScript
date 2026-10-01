"""Extract the public current event skin-box icon, not account data."""
from pathlib import Path
from PIL import Image

target = Path('assets/shop/event_kr/SkinBox__october.png')
if target.exists():
    raise SystemExit('Refusing to overwrite existing asset')
with Image.open('dev_tools/fixtures/kr_event_shop_design_counter.png') as source:
    source.crop((773, 242, 836, 305)).save(str(target))
