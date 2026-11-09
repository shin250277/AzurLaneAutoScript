"""Reviewed public labels from fixed recipes; never export account screens."""
from pathlib import Path
from hashlib import sha256
import sys
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

CASES = [
    ('601_9061', 'a0dce0bcd419e4957aecd79a8828aa1842dc37225a837ceb8c25a9f85272c219', 1, 3101, '정통 두부 세트'),
    ('603_9081', '3bb4a017d25d0ba4815dbc908e53efc7b7ab3d83cbb12635f0302ce4f733ebf0', 1, 3028, '딸기 샬럿'),
    ('704_9203', 'd911ff153977025d6b92c101ea69bfb9e6a90f8767fe6dcbbd41be7871029fc2', 0, 3045, '화학품'),
    ('706_9207', '9798b8a44018378e6c3ea7b95ca63834d1c9890ec8fa1cc3afefd46ef9c4b36b', 0, 3037, '밧줄'),
    ('706_9207', '9798b8a44018378e6c3ea7b95ca63834d1c9890ec8fa1cc3afefd46ef9c4b36b', 2, 3039, '향낭'),
    ('901_9041', 'af2c276d2c65dded2bf728e5511b34c1533c8f0bdc6a2ddf7c072818fc7461c0', 0, 3006, '치즈'),
]

if __name__ == '__main__':
    for suffix, digest, row, item_id, name in CASES:
        source = Path('log/kr_island_recipe_audit_%s.png' % suffix)
        if sha256(source.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Source changed; review required: ' + suffix)
        frame, buttons = grid(source)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_fixed_nov10_%s.png' % item_id)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_fixed_nov10_selected.png' % item_id)
