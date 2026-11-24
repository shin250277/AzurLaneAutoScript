"""Exercise the active UI page checks on private local screenshots, without a device."""
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
from PIL import Image
import module.config.server as server


def main(directory):
    server.set_server('kr')
    from module.ui import ui
    from module.ui import page as pages
    device = SimpleNamespace(stuck_record_add=lambda button: None)
    replay = object.__new__(ui.UI)
    replay.config = SimpleNamespace(SERVER='kr')
    replay.device = device
    pairs = """main2:main sortiemenu:campaign_menu campaign:campaign formation:fleet
        exercise:exercise exercise_again:exercise daily:daily opsi2:os archives:archives mission:mission
        guild:guild commission:commission tactical4:tactical dock:dock lab:research
        shipyard:shipyard meta2:meta storage:storage researchmenu:reshmenu
        living:dormmenu dorm3:dorm cats:meowfficer academy:academy shop:shop build:build
        mail:mail rewards:reward battlepass:battle_pass islandfloor:island
        islandmap:island_map islandseason:island_season islandtech:island_technology
        islandshop:island_shop islandmanage:island_phone islandorders:island_order
        islandstorage:island_storage islandtransport:island_transport mapagain:island_map
        storageagain:island_storage transport2:island_transport
        channelnow:channel eventlistnow:event_list gameroomlive:game_room
        munitionslive:munitions supplypacklive:supply_pack quarters:private_quarters
        islandassignment:island_manage"""
    pairs = [pair.split(':') for pair in pairs.split()]
    failures = []
    for frame, page in pairs:
        with Image.open(str(directory / (frame + '.png'))) as im:
            assert im.size == (1280, 720)
            device.image = np.asarray(im.convert('RGB'))
        matches = [name for name, candidate in pages.Page.all_pages.items()
                   if candidate.check_button and replay.ui_page_appear(candidate)]
        if matches != ['page_' + page]:
            failures.append('{}: expected {}, got {}'.format(frame, page, matches))
    print('Expected page detected: %d/%d. Misses: %s' %
          (len(pairs)-len(failures), len(pairs), ', '.join(failures)))
    return int(bool(failures))


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1])))
