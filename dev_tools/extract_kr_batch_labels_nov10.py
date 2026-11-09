"""Reviewed public labels from the 08:34-08:38 local failures; no account data."""
from PIL import Image
from pathlib import Path
from hashlib import sha256
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

CASES = [('603_9081', 1, 3025, '망고 찹쌀밥'),
         ('604_9091', 0, 3034, '햄버그 덮밥'),
         ('604_9091', 1, 3115, '레몬 새우'),
         ('703_9201', 0, 3050, '책상과 의자'),
         ('703_9201', 1, 3051, '특선 나무통'),
         ('704_9203', 1, 3044, '못'),
         ('706_9207', 0, 3037, '밧줄'),
         ('901_9041', 0, 3059, '오믈렛')]

DIGESTS = {
    '603_9081': '3229529f3d91f152db7bede50520753266b6375e92d2616fbf2e79fe28484a4d',
    '604_9091': 'af5e7caf968179ac63fe6d514715582b9ab694df0ebcab7816c155d8419f7d44',
    '703_9201': 'b7552b3113d561e53e3fe3f8a40c97a8891ce25e0d3bf6d299be134c2864e166',
    '704_9203': 'b98512345e1e8fc7ecac3fa884216e6e7cfcea2836b39d8533029b1e406adef7',
    '706_9207': '8fbc0ca40c8c3ebbed9a6a6d1de36086208acf7286d3dc39b538a25955b8e019',
    '901_9041': 'ec20c83c7d6f13f10d772e2883baa174c2c4acbbc6ad55b5fc8ad62a1352c4fc',
}

if __name__ == '__main__':
    import sys
    for suffix, row, item, _ in CASES:
        source = Path('log/kr_island_recipe_audit_%s.png' % suffix)
        assert sha256(source.read_bytes()).hexdigest() == DIGESTS[suffix], suffix
        frame, buttons = grid(source)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_batch_nov10_%s.png' % item)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_batch_nov10_selected.png' % item)
