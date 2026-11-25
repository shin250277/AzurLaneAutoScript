"""Reviewed Nov10 whole public labels for fractional-scroll renderings."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

SAMPLES = [
    ('603_9081','aa453348f21ca8933c28c2a5f2d9598d8283870d2a12f01b034d96518c8fbc8f',1,3025),
    ('703_9202','35aed3d3e86980f82fc4566c66f2779e119e6da44b02fa14d1e8141473a694cb',0,3048),
    ('901_9041','b4c3796cf7280777c1d91edd0c15ef086e5bb3cf8e6915b56420b252d92ab8b1',1,3007),
    ('dispatch_9061','5b8fd168dc28d2c5f40a973f104f92db2e2c05bba25213865f348aabb4cadc6c',1,3014),
]
if __name__ == '__main__':
    for suffix,digest,row,item in SAMPLES:
        path=Path('log/kr_island_dispatch_name_9061.png' if suffix=='dispatch_9061'
                  else 'log/kr_island_recipe_audit_%s.png'%suffix)
        if sha256(path.read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Changed frame requires review')
        frame,buttons=grid(path)
        label=crop(frame,buttons.crop((123,19,269,50)).buttons[row].area)
        icon=crop(frame,buttons.crop((20,20,115,115)).buttons[row].area)
        Image.fromarray(label).save('assets/kr/island_item_name/%s_nov10_evening_selected.png'%item)
        Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_evening_%s_name.png'%item)
        Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_evening_%s_icon.png'%item)
        if item in (3048,3007,3014):
            Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/%s.png'%item)
