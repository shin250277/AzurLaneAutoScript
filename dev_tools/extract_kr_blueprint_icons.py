"""Public generic ALL blueprint icons; deliberately do not infer series."""
from pathlib import Path
from PIL import Image
from dev_tools.check_kr_event_shop_frame import scan_frame

frame, grid = scan_frame('dev_tools/fixtures/kr_event_shop_blueprint_unknown.png')
for index, name in ((1, 'PRSeriesUnknown'), (2, 'DRSeriesUnknown')):
    target = Path('assets/shop/event_kr/%s__october.png' % name)
    if target.exists():
        raise SystemExit('Refusing to overwrite existing asset')
    x1, y1, x2, y2 = grid.grids.buttons[index].area
    Image.fromarray(frame[y1:y2, x1:x2]).save(str(target))
