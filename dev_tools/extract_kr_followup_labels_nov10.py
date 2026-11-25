"""Public whole labels reviewed in the 09:04-09:07 failures, not account data."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

CASES = [
    ('201_9211', 1, 5102, '삼치', 'ebc787ccc6b0e7558935450742fe3d3729ef69e46a1d23abe80743b05bfb19a1'),
    ('401_9011', 1, 2704, '황광석', '20057f552219252ba46dc14b57ce588ed4c286e5862cf831d108e00b5ea0a3cf'),
    ('601_9061', 0, 4009, '곶감', '2c0338422535ef0568bd9b2c5947f8faca24d9d361930b1bba9ae4e044fd42e3'),
    ('603_9081', 0, 3028, '딸기 샬럿', 'f7c4b0599ff829169b9868a8e56bbc850501fa3ec38b66d66cb4e0c7886bdc2e'),
    ('704_9203', 0, 3044, '못', '68048296306f9b6746cae2d522199bb070763844a1ff8de119f38909f6018a8e'),
    ('706_9207', 0, 3037, '밧줄', '7d06a0c111ca3a67d609ad18a8483bdcd5e6b2ac96ca65b01f269465611de617'),
    ('901_9041', 1, 3010, '딸기 밀크쉐이크', '3cced8428a239b947ab91f39f894e8aaf7616d12a3aa3b8bf52a387ec35dfb3d'),
]

if __name__ == '__main__':
    import sys
    for suffix, row, item, name, digest in CASES:
        source = Path('log/kr_island_recipe_audit_%s.png' % suffix)
        assert sha256(source.read_bytes()).hexdigest() == digest, suffix
        frame, buttons = grid(source)
        label = Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_followup_nov10_%s.png' % item)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_followup_nov10_0910_selected.png' % item)
