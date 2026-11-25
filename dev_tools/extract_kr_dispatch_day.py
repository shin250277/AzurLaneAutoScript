from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

if __name__ == '__main__':
    for slot,item in [(9061,3120),(9213,5103)]:
        path=Path('log/kr_island_dispatch_name_%s.png'%slot)
        expected={9061:'3533b06c3a75ff3aa19eedc207f8f36a3b70d3996eadde7790a5cdaad96f9cf4',
                  9213:'c5de4e35e025e8f29482d7679f013c01c4d235e4add0ef29e3f3525746a6fe4b'}
        if sha256(path.read_bytes()).hexdigest()!=expected[slot]:
            raise RuntimeError('Source changed; review again')
        frame,buttons=grid(path)
        label=crop(frame,buttons.crop((123,19,269,50)).buttons[1].area)
        icon=crop(frame,buttons.crop((20,20,115,115)).buttons[1].area)
        if item == 3120:
            Image.fromarray(label).save('assets/kr/island_item_name/3120_nov10_day_selected.png')
        else:
            Image.fromarray(icon[8:76,8:84]).save('assets/kr/island_recipe_icon/5103.png')
        Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_day_%s_name.png'%item)
        Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_day_%s_icon.png'%item)
