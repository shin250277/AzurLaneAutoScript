"""Extract public artwork only from locally reviewed November shop captures."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
import numpy as np
from module.base.utils import color_similarity_2d
from dev_tools.check_kr_event_shop_frame import scan_frame


def main():
    path = Path('log/kr_event_shop_scan_01.png')
    if sha256(path.read_bytes()).hexdigest() != 'f3930da1e569965a834ead46c9f75fbfd05b7f4b5f9e6f4fa5a2117fb288fc5d':
        raise ValueError('Changed top frame requires visual review')
    target = Path('assets/shop/event_kr_currency')
    with Image.open(str(path)) as source:
        source.convert('RGB').crop((947, 163, 973, 189)).save(str(target / 'guitar_pt__header.png'))
    frame, grid = scan_frame(path)
    grid.predict(frame, save_unknown=False)
    for index, item in enumerate(grid.items):
        pill = item.crop((-17, 120, 83, 149))
        mask = color_similarity_2d(pill, (61, 78, 91))
        ink = np.where(np.min(mask[9:19], axis=0) < 230)[0]
        if not len(ink):
            raise ValueError('Missing reviewed guitar token')
        left = int(ink[0])
        Image.fromarray(pill[4:26, left:left + 22]).save(str(target / ('guitar_pt__nov20_%02d.png' % index)))
    path = Path('log/kr_event_shop_scan_07.png')
    if sha256(path.read_bytes()).hexdigest() != '8fd5c4eb27f4349dc030e3ee135d07c8fcf3c7aab042f70404d6e7b7383ce2d2':
        raise ValueError('Changed shifted frame requires visual review')
    source = Image.open(str(path)).convert('RGB')
    safe = Image.new('RGB', (1280, 720), 'white')
    safe.paste(source.crop((221, 369, 1049, 580)), (221, 369))
    safe.save('dev_tools/fixtures/kr_event_shop_sold_out_shifted.png')


if __name__ == '__main__':
    main()
