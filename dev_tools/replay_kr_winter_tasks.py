"""Replay saved season cards; never connect to a device or account config."""
import argparse
from pathlib import Path
from types import SimpleNamespace

from module.config.server import set_server
set_server('kr')
from module.base.utils import load_image, crop
from module.island.season_task import IslandSeasonTask, NAME_AREA
from module.ocr.ocr import Ocr
from module.island.assets import TEMPLATE_ISLAND_SEASON_TASK_OBTAINED


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-reviewed-labels', action='store_true')
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    if args.extract_reviewed_labels:
        from PIL import Image
        import hashlib
        # Visually reviewed public title text only; no account values or artwork.
        for page, task, box, digest in [
                (3, 80001511, (470, 266, 592, 293), '9f712061971cd98046efc3c6480a1319411ff8144d30477fc62fca7d14d4fa04'),
                (4, 80001514, (470, 311, 549, 338), 'd18f232861790908d82b7f7143ef10a66b19a165ace79428c18cf6d4d00d2f49')]:
            path = Path('log/kr_island_inspect_tasks_%02d.png' % page)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Inspection frame changed; review before extracting labels')
            with Image.open(str(path)) as frame:
                frame.crop(box).save('assets/kr/island_task_name/%s.png' % task)
    ui = object.__new__(IslandSeasonTask)
    ui.device = SimpleNamespace(image=None)
    seen = set()
    for path in sorted(Path('log').glob('kr_island_inspect_tasks_[0-9][0-9].png')):
        ui.device.image = load_image(str(path))
        grid = ui.get_season_task_grid().crop(NAME_AREA)
        frames = [crop(ui.device.image, button.area) for button in grid.buttons]
        names = ui.task_name_ocr.ocr(frames, direct_ocr=True)
        codes = [ui.task_name_to_codename(name) for name in names]
        if args.require_complete and (not codes or None in codes):
            raise ValueError('Unknown or missing task on ' + path.name)
        seen.update(codes)
        print(path.name, list(zip(names, codes)))
        if args.progress:
            cards = ui.get_season_task_grid()
            counter_grid = cards.crop((285, 18, 365, 48))
            counters = Ocr(counter_grid.buttons, lang='cnocr', letter=(102, 108, 112),
                           threshold=128, alphabet='0123456789/').ocr(ui.device.image)
            obtained = [TEMPLATE_ISLAND_SEASON_TASK_OBTAINED.match(crop(ui.device.image, b.area))
                        for b in cards.buttons]
            print('Progress (task, counter, already obtained):', list(zip(codes, counters, obtained)))
    if args.require_complete and seen != set(range(80001501, 80001531)):
        raise ValueError('Winter task coverage incomplete: %s' % sorted(seen))
    print('Distinct identified tasks:', len(seen))


if __name__ == '__main__':
    main()
