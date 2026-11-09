"""Only the visually reviewed public tuna label, no stock or account data."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop


if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_201_9211.png')
    if sha256(path.read_bytes()).hexdigest() != '63c865ac44e7661cf36cfb01e8ba6e1b21c5ff71759b990e82050f7cc8ef933a':
        raise RuntimeError('Changed source needs review')
    frame, buttons = grid(path)
    Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[0].area)).save(
        'dev_tools/fixtures/kr_tuna_nov9.png')
    Image.open('dev_tools/fixtures/kr_tuna_nov9.png').save(
        'assets/kr/island_item_name/5103_lower_nov9_selected.png')
