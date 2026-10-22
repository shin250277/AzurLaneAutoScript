"""Extract a public UI label only; never publish the observed account frame."""
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    for item_id, source, row in ((2603, 'milk', 0), (5005, 'shrimp', 0), (3011, 'tofu', 1)):
        target = Path('assets/kr/island_item_name/{}_order.png'.format(item_id))
        if target.exists():
            continue  # Never overwrite established templates.
        with Image.open('log/kr_order_{}_observed.png'.format(source)) as frame:
            if frame.size != (1280, 720):
                raise ValueError('Expected observed 1280x720 client image')
            frame.crop((1052, 252 + row * 79, 1212, 280 + row * 79)).convert('RGB').save(str(target))
