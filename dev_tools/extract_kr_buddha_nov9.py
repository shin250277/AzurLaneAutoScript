"""Extract one reviewed public label, excluding stock and account information."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid


if __name__ == '__main__':
    source = Path('log/kr_island_recipe_audit_601_9062.png')
    if sha256(source.read_bytes()).hexdigest() != '69879d9e88fecfbc74b5346af7b961fbc2ff56c8b851524fd84128063caa3096':
        raise RuntimeError('Changed source requires visual review')
    frame, buttons = grid(source)
    label = Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[1].area))
    label.save('dev_tools/fixtures/kr_buddha_nov9.png')
    label.save('assets/kr/island_item_name/3120_lower_nov9_selected.png')
