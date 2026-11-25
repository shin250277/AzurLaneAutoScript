"""Extract public wheat-seed label only, without currency balance or account UI."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
import sys

if __name__ == '__main__':
    path = Path('log/kr_island_material_info.png')
    assert sha256(path.read_bytes()).hexdigest() == 'edd03ee2e70e3513348689deb0021deb76b298d91825ea28c6c7c1aad9c883fb'
    label = Image.open(str(path)).crop((236, 326, 358, 347))
    label.save('dev_tools/fixtures/kr_wheat_seed_shop.png')
    if '--install' in sys.argv:
        Path('assets/kr/island_shop_name').mkdir(exist_ok=True)
        label.save('assets/kr/island_shop_name/411000_wheat_selected.png')
