"""Public name-only observations; optional exact observed tuna reference."""
import sys
from pathlib import Path
from hashlib import sha256
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

if __name__ == '__main__':
    for path, digest, row, name in [
        ('log/kr_island_recipe_audit_901_9041.png', 'ee2cbccd8d08a6381a505b29d686523ceba7f9dcd8d27a35238f13d68ef0b2f5', 1, 'latte'),
        ('log/kr_island_recipe_unknown.png', '054630b2dbaf49f769975afacbdfe54460cf2529a7682f9d60cf41fd5ffef4f9', 2, 'tuna')]:
        assert sha256(Path(path).read_bytes()).hexdigest() == digest
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_adaptive_%s.png' % name)
        if name == 'tuna' and '--install' in sys.argv:
            label.save('assets/kr/island_item_name/5103_bright_nov10_selected.png')
