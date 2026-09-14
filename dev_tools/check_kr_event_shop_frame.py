"""Read-only event-shop recognition diagnostic for a saved Korean frame."""
import argparse
from types import SimpleNamespace

import numpy as np
from PIL import Image


def scan_frame(path):
    import module.config.server as server
    server.server = 'kr'
    from module.shop_event.clerk import EventShopClerk
    from module.shop_event.item import EventShopItemGrid
    frame = np.array(Image.open(str(path)).convert('RGB'))
    if frame.shape != (720, 1280, 3):
        raise ValueError('Expected 1280x720 game frame')
    observer = SimpleNamespace(device=SimpleNamespace(image=frame))
    grid = EventShopClerk._get_event_shop_grid(observer)
    items = EventShopItemGrid(grid, {})
    items.load_template_folder('./assets/shop/event')
    return frame, items


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    args = parser.parse_args()
    frame, grid = scan_frame(args.frame)
    # Disable classification side effects (unknown-template writing) here.
    from module.statistics.item import ItemGrid
    ItemGrid.predict(grid, frame, price=True)
    for item in grid.items:
        print(item.button, str(item))
