from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_603_9081.png')
    if sha256(path.read_bytes()).hexdigest() != '39118876f22fe36972dedeca94953ac2ae654d14b008f1dce14f9e2d22d43336':
        raise RuntimeError('Changed source requires review')
    frame, buttons = grid(path)
    label = crop(frame,buttons.crop((123,19,269,50)).buttons[0].area)
    icon = crop(frame,buttons.crop((20,20,115,115)).buttons[0].area)
    Image.fromarray(label).save('assets/kr/island_item_name/3009_nov10_apple_selected.png')
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/3009.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_apple_3009_name.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_apple_3009_icon.png')
    path = Path('log/kr_island_recipe_audit_703_9202.png')
    if sha256(path.read_bytes()).hexdigest() != '5e26b4e844030f6c792e7fcc380d1c0bd564bd32a9e06c347c285ab4786e9363':
        raise RuntimeError('Changed notebook source requires review')
    frame, buttons = grid(path)
    label = crop(frame,buttons.crop((123,19,269,50)).buttons[0].area)
    icon = crop(frame,buttons.crop((20,20,115,115)).buttons[0].area)
    Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/3049.png')
    Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_notebook_3049_name.png')
    Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_notebook_3049_icon.png')
