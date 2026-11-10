from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if sha256(path.read_bytes()).hexdigest() != '4be0e6ee8b99eb28e3c599226dce3bcd82e7e8bf5aec939feca9b1fa3b752f3e':
        raise RuntimeError('Changed source requires review')
    frame, buttons = grid(path)
    for kind, area in [('icon', (20,20,115,115)), ('name', (123,19,269,50))]:
        Image.fromarray(crop(frame, buttons.crop(area).buttons[2].area)).save(
            'dev_tools/fixtures/kr_nov10_joint_bright_mango_%s.png' % kind)
    path = Path('log/kr_island_recipe_audit_706_9207.png')
    if sha256(path.read_bytes()).hexdigest() != '8c9c4bade2787692e1d7442678b0be5bfae00dbdde5ad01471e43856793485ab':
        raise RuntimeError('Changed cloth source requires review')
    frame, buttons = grid(path)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[0].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3035_nov10_night_selected.png')
