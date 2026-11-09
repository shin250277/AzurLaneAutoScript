"""Extract visually reviewed public item names only, never account data."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid


if __name__ == '__main__':
    for name, digest, row, item in [
        ('601_9061', 'cbedd92042d0a6a2d183fed093f1fed2fe38118addc0020f4221dd8bdc37c96a', 1, 3114),
        ('102_9034', '5470d65fec4713b632c7aad40e4ae489cad69f36306a24eecc846662b491e931', 0, 2605),
    ]:
        path = Path('log/kr_island_recipe_audit_%s.png' % name)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires visual review')
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_evening_%s.png' % item)
        label.save('assets/kr/island_item_name/%s_evening_selected.png' % item)
