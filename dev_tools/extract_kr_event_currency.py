"""Public event-token artwork only, from existing sanitized regression frames."""
from pathlib import Path
from PIL import Image
import numpy as np
from module.base.utils import crop, color_similarity_2d
from dev_tools.check_kr_event_shop_frame import scan_frame


if __name__ == '__main__':
    folder = Path('assets/shop/event_kr_currency')
    folder.mkdir(exist_ok=True)
    for source, box, name in [
            ('kr_event_shop_top.png', (268, 369, 287, 380), 'train_pt'),
            ('kr_event_shop_top.png', (947, 169, 972, 182), 'train_pt__header'),
            ('kr_event_shop_design_counter.png', (431, 369, 450, 387), 'skull_pt')]:
        with Image.open('dev_tools/fixtures/' + source) as frame:
            frame.convert('RGB').crop(box).save(str(folder / (name + '.png')))
    # Every displayed card in these two reviewed, sanitized fixtures uses the
    # same public event token. Capture raster variants, NOT price digits.
    for filename, token in [('kr_event_shop_top.png', 'train_pt'),
                            ('kr_event_shop_design_counter.png', 'skull_pt'),
                            ('kr_event_shop_middle.png', 'train_pt'),
                            ('kr_event_shop_middle_shifted.png', 'train_pt'),
                            ('kr_event_shop_bottom.png', 'train_pt'),
                            ('kr_event_shop_bottom_shifted.png', 'train_pt')]:
        frame, grid = scan_frame('dev_tools/fixtures/' + filename)
        grid.predict(frame, save_unknown=False)
        for index, item in enumerate(grid.items):
            pill = item.crop((-17, 120, 83, 149))
            mask = color_similarity_2d(pill, (61, 78, 91))
            ink = np.where(np.min(mask[9:19], axis=0) < 230)[0]
            if not len(ink):
                raise ValueError('Missing reviewed token')
            left = int(ink[0])
            Image.fromarray(pill[4:26, left:left+22]).save(
                str(folder / ('%s__%s_%02d.png' % (token, Path(filename).stem, index))))
