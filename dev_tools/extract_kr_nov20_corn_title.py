"""Extract only the reviewed public corn-cup title, not account pixels."""
import hashlib
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != 'eccb9776a4027fa622c9c43a4a3b9e5cbc06da295aba6a0f36f987abfa96e3ba':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304,272,450,303)).save(
            'assets/kr/island_item_name/3023_nov20_afternoon_selected.png')
