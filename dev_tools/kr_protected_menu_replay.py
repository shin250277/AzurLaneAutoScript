"""Verify dock filters, battle-pass navigation and paid-pack negatives without clicking."""
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
from module.config import server


def load(path):
    with Image.open(str(path)) as image:
        return np.array(image.convert('RGB'))


def run(root):
    server.set_server('kr')
    from module.retire.dock import Dock
    from module.guild.logistics import GuildLogistics, GUILD_EXCHANGE_LIMIT
    from module.storage.ui import StorageUI, DISASSEMBLE, DISASSEMBLE_CANCEL
    from module.freebies.assets import FREE_SUPPLY_PACK
    from module.ui.assets import BATTLE_PASS_CHECK, REWARD_GOTO_BATTLE_PASS
    menu = root / 'kr_menu_capture_20261122'
    dock = object.__new__(Dock)
    dock.config = SimpleNamespace(SERVER='kr')
    dock.device = SimpleNamespace(stuck_record_add=lambda button: None)
    expected = {('sort', 'level'), ('index', 'all'), ('faction', 'all'),
                ('rarity', 'all'), ('extra', 'no_limit')}
    for name in ('dockfilter', 'dockfilter2'):
        dock.device.image = load(menu / (name + '.png'))
        setting = dock.dock_filter
        active = {k for k, b in setting.settings.items() if setting.is_option_active(b)}
        assert active == expected, (name, active)
    for name in ('main2', 'rewards', 'battlepass'):
        im = load(menu / (name + '.png'))
        assert REWARD_GOTO_BATTLE_PASS.match(im, (50, 150)) == (name == 'rewards'), name
        assert BATTLE_PASS_CHECK.match(im, (20, 20)) == (name == 'battlepass'), name
    packs = sorted(root.glob('kr_supply_inspect_*.png'))
    assert len(packs) == 12
    for p in packs:
        assert not FREE_SUPPLY_PACK.match(load(p), (200, 20)), p.name
    guild = object.__new__(GuildLogistics)
    guild.config, guild.device = dock.config, dock.device
    for name, selected in [('home', 0), ('logistics', 2), ('tech', 3)]:
        guild.device.image = load(root / 'kr_inner_20261124' / ('guild_' + name + '.jpg'))
        assert guild._guild_side_navbar.get_info(guild) == (selected, 0, 4), name
        assert guild._is_in_guild_logistics() == (name == 'logistics'), name
        if name == 'logistics':
            assert GUILD_EXCHANGE_LIMIT.ocr(guild.device.image) == 3
            assert not guild._guild_logistics_mission_available()
            assert guild._guild_logistics_supply_available()
    storage = object.__new__(StorageUI)
    storage.config, storage.device = dock.config, dock.device
    for name in ('material', 'blueprint', 'equipment'):
        storage.device.image = load(root / 'kr_inner_20261124' / ('storage_' + name + '.jpg'))
        assert storage._storage_in_material() == (name == 'material'), name
        assert storage.appear(DISASSEMBLE, offset=(20, 20)) == (name == 'equipment'), name
        assert not storage.appear(DISASSEMBLE_CANCEL, offset=(20, 20)), name
    print('Dock: %d options x 2 frames; pass navigation: 6; paid-pack negatives: 12; OK'
          % len(setting.settings))


if __name__ == '__main__':
    run(Path(sys.argv[1]))
