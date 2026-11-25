"""Read only local KR logistics frames; never submit a donation to obtain a sample."""
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image


def run(root):
    from module.config import server
    server.set_server('kr')
    from module.guild.logistics import GuildLogistics, GUILD_EXCHANGE_LIMIT
    from module.ui.page import page_guild
    guild = object.__new__(GuildLogistics)
    guild.config = SimpleNamespace(SERVER='kr')
    guild.device = SimpleNamespace(stuck_record_add=lambda button: None)
    states = Counter()
    for path in root.rglob('*'):
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        with Image.open(str(path)) as image:
            if image.size != (1280, 720):
                continue
            guild.device.image = np.asarray(image.convert('RGB'))
        if guild.ui_page_appear(page_guild) and guild._is_in_guild_logistics():
            value = GUILD_EXCHANGE_LIMIT.ocr(guild.device.image)
            states[value] += 1
            print(value, path)
    print('Guild logistics candidates (OCR, not independently labelled):', dict(states))


if __name__ == '__main__':
    import sys
    run(Path(sys.argv[1]))
