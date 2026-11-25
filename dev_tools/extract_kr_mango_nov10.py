"""Reviewed public mango label/artwork; never export the account frame."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if sha256(path.read_bytes()).hexdigest() != 'cebe377e494232d2a1ced172fe760faae4a1a5eae4f9ab85918b76b6602f9964':
        raise RuntimeError('Source changed; review again')
    frame, buttons = grid(path)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[1].area)
    icon = crop(frame, buttons.crop((20,20,115,115)).buttons[1].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3025_nov10_mango_selected.png')
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/3025.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_mango_3025_name.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_mango_3025_icon.png')
    path = Path('log/kr_island_recipe_audit_706_9207.png')
    if sha256(path.read_bytes()).hexdigest() != '4abb4263b4e8775df85d70468c579c9d5e6769a0414aa145bf3f4aa44751a738':
        raise RuntimeError('Glove source changed; review again')
    frame, buttons = grid(path)
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[0].area)
    icon = crop(frame, buttons.crop((20,20,115,115)).buttons[0].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3038_nov10_gloves_selected.png')
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/3038.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_gloves_3038_name.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_gloves_3038_icon.png')
