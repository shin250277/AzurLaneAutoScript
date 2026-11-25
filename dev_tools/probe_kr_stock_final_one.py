"""Offline numeric crop context probe; never opens a game device."""
import numpy as np
from PIL import Image
from pathlib import Path
from module.base.utils import crop
from module.island_handler.korean_stock import KoreanRecipeStockDigit
from module.ocr.ocr import Digit
from dev_tools.extract_kr_recipe_followup_nov9 import grid

frame, buttons = grid(Path('log/kr_island_stock_unknown.png'))
sample = crop(frame, buttons.crop((212, 92, 275, 114)).buttons[0].area)
import sys
if '--fixture' in sys.argv:
    from hashlib import sha256
    if sha256(Path('log/kr_island_stock_unknown.png').read_bytes()).hexdigest() != '3951cc0d6c4ae112d053925e66c60d7eae93a97b6e408b8e36e23274ee73bc4c':
        raise ValueError('Changed source requires review')
    Image.fromarray(sample).save('dev_tools/fixtures/kr_stock_final_one.png')
base = KoreanRecipeStockDigit([], lang='cnocr', letter=(80,80,80), threshold=160)
prepared = base.pre_process(sample)[4:-4, 4:-4]
for padding in (0, 1, 2, 3, 4, 6, 8, 10):
    reader = Digit([], lang='cnocr')
    reader.pre_process = lambda image, p=padding: np.pad(prepared, ((p,p),(p,p)), mode='constant', constant_values=255)
    print(padding, reader.ocr([sample], direct_ocr=True))
