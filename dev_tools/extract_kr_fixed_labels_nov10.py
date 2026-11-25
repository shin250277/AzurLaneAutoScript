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
    ('602_9071', 'a066341436455abfe80ba9185b92ee6761b7c676a25d830104185e0090cbc76b', 2, 3019, '꿀 레몬 워터'),
    ('703_9201', '5bc38919aec415454cc9961ae79d26dc2a392758d0fed34d85953a51bdb8c8f5', 0, 3051, '특선 나무통'),
    ('501_9101', 'e9fdabde5a81415b1d77514ff55d5a6130e0f526797ea762b8054fed4f94e065', 1, 2017, '감귤'),
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
    source = Path('log/kr_island_recipe_audit_604_9091.png')
    if sha256(source.read_bytes()).hexdigest() != '7a18092c01bb67058d41076ddd6c7d49be3e2ca287825ef932f2ac736623f1db':
        raise RuntimeError('Changed omelet frame; review required')
    frame, buttons = grid(source)
    icon = Image.fromarray(crop(frame, buttons.crop((20,20,115,115)).buttons[1].area))
    icon.save('dev_tools/fixtures/kr_omelet_icon_nov10.png')
    if '--install' in sys.argv:
        # Only public artwork, excluding border, quantity and selected state.
        icon.crop((8,8,84,76)).save('assets/kr/island_recipe_icon/3033.png')
