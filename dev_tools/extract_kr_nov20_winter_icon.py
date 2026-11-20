"""Reviewed public winter dish artwork; no account values are exported."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_601_9061.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '68dad913622e9ff1a3aa17784a620a36f029f6a97d45f83b074e7ffb995330e8':
        raise ValueError('Frame changed; review first')
    # Selected winter shiitake/chicken dish: visible title and the selected
    # ingredient pair (winter shiitake x2, chicken x1) agree with recipe9900027.
    # Matching still requires separately read title text, never artwork alone.
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((201, 134, 296, 229)).save(
            'assets/kr/island_recipe_icon/4051.png')
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '5f4a1a52647b49f674535723070e348a4e6d2355edceb497c56cea9660779992':
        raise ValueError('Dessert frame changed; review first')
    with Image.open(str(path)) as frame:
        for item, y in ((4053, 133), (4054, 282)):
            frame.convert('RGB').crop((304, y, 450, y + 31)).save(
                'assets/kr/island_item_name/%s_nov20_selected.png' % item)
