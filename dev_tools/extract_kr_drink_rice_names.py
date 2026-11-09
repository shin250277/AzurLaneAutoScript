"""Extract only visually reviewed public recipe labels; never full frames."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop


if __name__ == '__main__':
    for source, digest, row, item in [
        ('602_9071', '4c4446118e7c1921a41e0631d5646027eb091db1bf5e0fb8777e7430701e9500', 0, 3019),
        ('603_9081', 'd8ae3ce6292e138cae1192fc53ebaa223ad7e36db6b43a628ca9f3c8be1a8f13', 1, 3025),
        ('604_9091', 'a42947f31a3687ac8456e0e1e726f03ce18d397370cb7605ca958ec872cc721a', 1, 3109),
        ('703_9201', 'b98aecbd926bcbbf25d852215c7f9ebf0d8df11277c0fd3188d5f521cc191a63', 2, 3052),
        ('704_9203', '6e0dbce401b55519ebf162a5635aa8aa8ac0f1b9220dea5d4adb4558f712ab0f', 0, 3044),
        ('901_9041', '270a918c8cf74466082f8111cea7e59abb0fa9fb873926e6e7e49e6a521bbf64', 1, 3007),
        ('706_9207', 'bd00b629d0b1d62a7b4b4ebcb04cf052b21153fa24816348b8b0bf641696a2c3', 2, 3037),
    ]:
        path = Path('log/kr_island_recipe_audit_%s.png' % source)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed frame requires review')
        im, buttons = grid(path)
        Image.fromarray(crop(im, buttons.crop((123,19,269,50)).buttons[row].area)).save(
            'dev_tools/fixtures/kr_recipe_name_nov9_%s.png' % item)
        Image.open('dev_tools/fixtures/kr_recipe_name_nov9_%s.png' % item).save(
            'assets/kr/island_item_name/%s_lower_nov9_selected.png' % item)
