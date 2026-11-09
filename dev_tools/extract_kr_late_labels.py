"""Extract reviewed public labels, never full account screens."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from module.base.utils import crop
from module.island.data import DIC_ISLAND_ITEM

CASES = [
    ('unknown', 'af26f42628f7f1bce207c4fe39e61413ad7651c2ebac697c7eec1006b0ed89ee', 0, 3019),
    ('604_9091', '0fbc5abf67093c3ac914b14b9bd6c4515574ae36506e428708811bc1e24fe7e1', 1, 3115),
    ('703_9201', 'a739058eb82ab03c441ab2d05b0f4f165faa3bafd114c7c6114cdaf673c325ad', 1, 3051),
    ('603_9081', 'e230f1310e95365d433148dd253314620d56260065dc0eafcb307dc4aabcf837', 0, 3025),
    ('501_9101', 'f9845cbed7eb237fe63656f2ef20a0386abbab5396600fcc37f2227a916c5293', 1, 2021),
    ('601_9061', 'e2dc6fda1d968172f3742cc28e2d1f33a5e5c1b0097146e13274fde0f6f65b3d', 1, 3114),
]
for group, digest, row, name in [
    ('704_9203', '11fd19c98581e4cef37e29f46f20a3b1526a6f9d5837b47c3e4243dd1ef0f1ae', 0, '못'),
    ('706_9207', 'b6b26a4fc57a63979b3627829e5adbb387a19d5da2acc274a77fdb22e0c37a0c', 1, '밧줄'),
    ('901_9041', 'd641eaed50e0fbe5cc0e68d2d2b677c0944683fba88638f731be093dee6e553c', 0, '딸기 밀크쉐이크'),
]:
    ids = [key for key, value in DIC_ISLAND_ITEM.items() if value['name'].get('kr') == name]
    assert len(ids) == 1, name
    CASES.append((group, digest, row, ids[0]))

if __name__ == '__main__':
    import sys
    from dev_tools.extract_kr_recipe_followup_nov9 import grid
    for name, digest, row, item in CASES:
        path = Path('log/kr_island_recipe_unknown.png' if name == 'unknown'
                    else 'log/kr_island_recipe_audit_%s.png' % name)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires visual review')
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_late_%s.png' % item)
        icon = Image.fromarray(crop(frame, buttons.crop((20, 20, 115, 115)).buttons[row].area))
        icon.save('dev_tools/fixtures/kr_late_%s_icon.png' % item)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_late_selected.png' % item)
