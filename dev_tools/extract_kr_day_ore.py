from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    path=Path('log/kr_island_recipe_audit_401_9012.png')
    if sha256(path.read_bytes()).hexdigest()!='832d8d4253eb4ac868c7b7474b28bb13193a0a1b39d279534c88693f2d7a46d0':
        raise RuntimeError('Changed source requires review')
    frame,buttons=grid(path)
    label=crop(frame,buttons.crop((123,19,269,50)).buttons[2].area)
    icon=crop(frame,buttons.crop((20,20,115,115)).buttons[2].area)
    Image.fromarray(label).save('assets/kr/island_item_name/2704_nov10_day_selected.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_day_2704_name.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_day_2704_icon.png')
