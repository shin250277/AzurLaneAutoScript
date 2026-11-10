from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop
if __name__ == '__main__':
    path=Path('log/kr_island_dispatch_name_9202.png')
    if sha256(path.read_bytes()).hexdigest()!='8c181e88b7c47edd2863737742dba6dcedfb808ece5031721b48685cb5d8d86a':
        raise RuntimeError('Changed source requires review')
    frame,buttons=grid(path)
    icon=crop(frame,buttons.crop((20,20,115,115)).buttons[1].area)
    label=crop(frame,buttons.crop((123,19,269,50)).buttons[1].area)
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/3052.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_joint_cabinet_icon.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_joint_cabinet_name.png')
