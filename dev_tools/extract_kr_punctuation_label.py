from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_unknown.png')
    if sha256(path.read_bytes()).hexdigest() != '0db7c4eef5e3131b60e7b32fc2395e3ffd45ec4c895f4610d6d8ed409baa4c2a':
        raise RuntimeError('Changed source requires review')
    frame, buttons = grid(path)
    Image.fromarray(crop(frame,buttons.crop((123,19,269,50)).buttons[1].area)).save(
        'dev_tools/fixtures/kr_cabbage_punctuation.png')
