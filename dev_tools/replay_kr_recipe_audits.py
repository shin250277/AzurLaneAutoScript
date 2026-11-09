"""Replay saved recipe identities through the runtime path, without a device.

Uses local failure images only. Never saves/exports frames or changes settings.
A static replay verifies identity logic, not live scrolling or stable captures.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe


def replay(path):
    frame, buttons = grid(path)
    device = Mock()
    ui = SimpleNamespace(
        recipe_grid=buttons, get_recipe_grid=lambda: buttons,
        image_crop=lambda area, copy=True: crop(frame, area, copy=copy),
        working_slot_id=int(path.stem.rsplit('_', 1)[1]),
        device=device, is_in_recipe_menu=lambda: True)
    result = IslandRecipe.get_recipe_ids(ui)
    device.click.assert_not_called()
    device.drag.assert_not_called()
    device.image_save.assert_not_called()
    return result


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    paths = sorted(Path('log').glob('kr_island_recipe_audit_*.png'))
    if not paths:
        raise SystemExit('No saved recipe audit frames')
    failures = []
    for path in paths:
        try:
            print(path.name, replay(path), flush=True)
        except Exception as exc:
            failures.append(path.name)
            print(path.name, type(exc).__name__, str(exc), flush=True)
    print('REPLAY frames=%s failed=%s' % (len(paths), failures), flush=True)
    sys.exit(bool(failures))
