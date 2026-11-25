"""Extract reviewed public labels, never account stock or full screenshots."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

SAMPLES = [
    ('706_9207', 'a427a4d023f232ffe051ab1055961a88800933b5ededc8b0ff11f64512addd6c', 3035),
    ('901_9041', 'eedefe8591eaa8726f2ecc1bb2c7acc156c7d12c081add0f1060a36bbcc630f6', 3006),
]

if __name__ == '__main__':
    for suffix, digest, item in SAMPLES:
        path = Path('log/kr_island_recipe_audit_%s.png' % suffix)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires review: %s' % path)
        frame, buttons = grid(path)
        label = crop(frame, buttons.crop((123, 19, 269, 50)).buttons[1].area)
        icon = crop(frame, buttons.crop((20, 20, 115, 115)).buttons[1].area)
        Image.fromarray(label).save('assets/kr/island_item_name/%s_nov10_day_selected.png' % item)
        Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_day_%s_name.png' % item)
        Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_day_%s_icon.png' % item)
        if item == 3006:
            Image.fromarray(icon[8:76, 8:84]).save('assets/kr/island_recipe_icon/3006.png')
