"""Extract only a visually reviewed public recipe title, never account data."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_201_9211.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '00e77f7460cf91fd5914f09c10c83de4cb0033abe8c23f0a6adf0f7f6e355a81':
        raise ValueError('Frame changed; visually review before extracting')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 259, 450, 290)).save(
            'assets/kr/island_item_name/5103_nov20_selected.png')
    for filename, digest, item, y in (
            ('kr_island_recipe_audit_703_9201.png',
             '5d548492fe2d934f7af72ad8c859747db7862d3827c71712065a9aa12da25e70', 3051, 239),
            ('kr_island_recipe_audit_704_9203.png',
             'a86a47aa736bd67e8f380f5f09f5715391e27ac168ebf2b2ef87d7bb79dd475b', 3044, 128),
            ('kr_island_recipe_audit_706_9207.png',
             'fa86386ae7a78aca93126cbf4b3ef669b5cd2eb34f8cc6aa642c3ab18430cea7', 4056, 282)):
        path = Path('log') / filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Frame changed; visually review first')
        with Image.open(str(path)) as frame:
            frame.convert('RGB').crop((304, y, 450, y + 31)).save(
                'assets/kr/island_item_name/%s_nov20_selected.png' % item)
