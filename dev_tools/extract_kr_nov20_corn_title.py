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
    path = Path('log/kr_island_dispatch_name_9091.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != 'acd96ee311acf4476e71519515f299eee66b6791e30b8e82cbbfd24cda0a4417':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304,298,450,329)).save(
            'assets/kr/island_item_name/3033_nov20_afternoon_selected.png')
    path = Path('log/kr_island_dispatch_name_9207.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != 'f51040e30cd50faa804913c5793f8aac8eb0f2e59b3ff9b98da709a1c3a866a9':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304,216,450,247)).save(
            'assets/kr/island_item_name/3035_nov20_dispatch_selected.png')
    path = Path('log/kr_island_dispatch_name_9041.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '601e90a7d174229906868ae03d3818d7cef97e69d01e90dd38d8acfd7d20c4ad':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304,550,450,581)).save(
            'assets/kr/island_item_name/3113_nov20_afternoon_selected.png')
