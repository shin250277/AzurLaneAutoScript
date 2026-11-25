"""Extract only the reviewed public ore label, never the account screen."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_401_9011.png')
    assert sha256(path.read_bytes()).hexdigest() == 'c882d8f073d2c43e5079f875888db7eaff5b02b89b9d38ba76b403970b9ea586'
    frame, buttons = grid(path)
    Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[2].area)).save(
        'dev_tools/fixtures/kr_bright_ore_nov10.png')
