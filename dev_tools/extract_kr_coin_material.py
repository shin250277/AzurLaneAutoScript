"""Extract only public dialog labels/icons; never account state or full frames."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from module.island_handler.kr_coin_material import AREAS

if __name__ == '__main__':
    source = Path('log/kr_island_material_purchase.png')
    assert sha256(source.read_bytes()).hexdigest() == 'fe400c4cc9e35aa6badaed2382d01043c36b0a17f3f716353f6f82ab4e4c3c30'
    frame = Image.open(str(source))
    dest = Path('assets/kr/island_material')
    dest.mkdir(exist_ok=True)
    for name, area in AREAS.items():
        frame.crop(area).save(str(dest / (name + '.png')))
    frame.crop((623, 184, 730, 212)).save('dev_tools/fixtures/kr_wheat_seed_dialog.png')
    import sys
    if '--install' in sys.argv:
        frame.crop((623, 184, 730, 212)).save('assets/kr/island_shop_name/411000_dialog_selected.png')
