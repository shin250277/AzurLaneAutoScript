"""Public token variants from five visually reviewed scroll pages."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
import numpy as np
from module.base.utils import color_similarity_2d
from dev_tools.check_kr_event_shop_frame import scan_frame


def main():
    hashes = (
        'd0742bcb6b0b37ffcc45a48d7260d3603927a518276f963a5f2c6b922fc6a160',
        'cfcfca999a9f5f0116ddb60c9803ed6725b494397ba992e3d0c62e474025e468',
        '089326fc46d2c6eee18c0af4c6ab94971e71c5d755765be7e2e84db95a5f66d5',
        '0edef70318ace8f258a241a9f8582e131353333520383b588ee921c55175099e',
        '0400ec93a0ca69f6ec0dd2fe3979d73b682de12ff0e1781132263e4a77e4b242',
    )
    for page in range(2, 7):
        source = Path('log/kr_event_shop_scan_%02d.png' % page)
        if sha256(source.read_bytes()).hexdigest() != hashes[page - 2]:
            raise ValueError('Changed source requires visual review')
        frame, grid = scan_frame(source)
        grid.predict(frame, save_unknown=False)
        for index, item in enumerate(grid.items):
            pill = item.crop((-17, 120, 83, 149))
            mask = color_similarity_2d(pill, (61, 78, 91))
            left = int(np.where(np.min(mask[9:19], axis=0) < 230)[0][0])
            Image.fromarray(pill[4:26, left:left + 22]).save(
                'assets/shop/event_kr_currency/guitar_pt__scroll_%02d_%02d.png' % (page, index))


if __name__ == '__main__':
    main()
