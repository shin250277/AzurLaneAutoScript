"""Reviewed single public item label; no account or stock pixels exported."""
import hashlib
from pathlib import Path
from PIL import Image

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_704_9203.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '2ed35dc1a1516c7ebc67e73df1ae656df286fab1d89486b38a97d31d0f20c2a9':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 340, 450, 371)).save(
            'assets/kr/island_item_name/3044_nov20_followup.png')
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '34d5273574e019a56c46a9c99b11032f1e45ec8502244a106682400bcbd42295':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 275, 450, 306)).save(
            'assets/kr/island_item_name/3009_nov20_followup.png')
    path = Path('log/kr_island_recipe_audit_604_9091.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '50f9aeccf51b53860c6338be280e5c13bad76ed53f9426852691fcfbc41ba495':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 263, 450, 294)).save(
            'dev_tools/fixtures/kr_lemon_shrimp_bright_title.png')
    path = Path('log/kr_island_recipe_audit_706_9207.png')
    if hashlib.sha256(path.read_bytes()).hexdigest() != '0b0592e949d3c2738b2a90c932c58b86591f3b828e4a7c61df34e5b15207d660':
        raise ValueError('Changed frame requires review')
    with Image.open(str(path)) as frame:
        frame.convert('RGB').crop((304, 415, 450, 446)).save(
            'assets/kr/island_item_name/3035_nov20_followup_selected.png')
