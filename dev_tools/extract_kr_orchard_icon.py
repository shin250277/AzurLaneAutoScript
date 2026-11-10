from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_501_9101.png')
    if sha256(path.read_bytes()).hexdigest() != 'd34bd9f755f0127307cb0dd098f075bc62b9836d312e5fafffe34a4fce413965':
        raise RuntimeError('Changed source requires review')
    frame, buttons = grid(path)
    icon = crop(frame, buttons.crop((20,20,115,115)).buttons[1].area)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[1].area)
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/2017.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_orchard_icon.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_orchard_name.png')
    Image.fromarray(label).save('assets/kr/island_item_name/2017_nov10_night_selected.png')
    path = Path('log/kr_island_dispatch_name_9081.png')
    if sha256(path.read_bytes()).hexdigest() != 'a58349e4abed53e6141117cdf0cf6e942e6ff995e2f1b86cfd4f72072446a491':
        raise RuntimeError('Changed strawberry charlotte source requires review')
    frame, buttons = grid(path)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[2].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3028_nov10_night_selected.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_charlotte_name.png')
    path = Path('log/kr_island_dispatch_name_9207.png')
    if sha256(path.read_bytes()).hexdigest() != '8f48500cbe39383b88e6298d68c26543e3dc17017b79b60975b97483c5cbe1cb':
        raise RuntimeError('Changed dispatch cloth source requires review')
    frame, buttons = grid(path)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[0].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3035_nov10_dispatch_selected.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_dispatch_cloth_name.png')
