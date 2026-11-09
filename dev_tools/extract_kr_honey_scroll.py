"""Extract reviewed public recipe text, not account data or full screenshots."""
from hashlib import sha256
from pathlib import Path
import sys
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

if __name__ == '__main__':
    source = Path('log/kr_island_recipe_audit_602_9072.png')
    if sha256(source.read_bytes()).hexdigest() != '470daffe157a1d0281fb1f018b5067ef4e22a0ff2051b8128f9c87e1010cc4c9':
        raise RuntimeError('Source changed; review before extracting')
    frame, buttons = grid(source)
    label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[1].area))
    label.save('dev_tools/fixtures/kr_honey_scroll_nov9.png')
    if '--install' in sys.argv:
        label.save('assets/kr/island_item_name/3019_scroll_nov9_selected.png')
