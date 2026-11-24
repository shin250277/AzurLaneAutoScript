"""Replay four KR shops without purchasing; optional extraction saves labelled icons only."""
import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
from dev_tools.kr_protected_menu_replay import load
from module.config import server


def run(folder, extract=False):
    server.set_server('kr')
    from module.shop.shop_merit import MeritShop_250814
    shop = object.__new__(MeritShop_250814)
    shop.config = SimpleNamespace(SERVER='kr', SHOP_EXTRACT_TEMPLATE=False, MeritShop_BuyUnobtainedShip=False)
    expected = ('BulinT2 BulinT1 Albacore Z28 Casablanca BoxT2 BoxT2 BoxIrisT2 BoxT1 BoxT1').split()
    prices = [15000, 3000, 20000, 8000, 5000, 300, 300, 400, 100, 100]
    if extract:
        grid = shop.shop_items()
        im = load(folder / 'merit_clean.png')
        for index, pos in [(0, (0, 0)), (7, (2, 1))]:
            path = Path(shop.shop_template_folder) / (expected[index] + '_3.png')
            icon = grid.item_class(im, grid.grids[pos]).image
            if path.exists():
                assert np.array_equal(icon, load(path)), path
            else:
                Image.fromarray(icon).save(str(path))
        del shop.__dict__['shop_merit_items']
    items = shop.shop_detect_items(load(folder / 'merit_clean.png'))
    assert [v.name for v in items] == expected
    assert [v.price for v in items] == prices
    assert all(v.cost == 'Merit' and not shop.shop_check_custom_item(v) for v in items)
    print('KR merit shop: 10/10 names, prices and currencies; no purchase action.')
    from module.shop.shop_general import GeneralShop_250814
    from module.shop.shop_core import CoreShop_250814
    from module.shop.shop_guild import GuildShop_250814
    for cls, frame, currency, prices in (
        (CoreShop_250814, 'coremonthly_clean', 'Core', [35, 500, 1500] + [800] * 7),
        (GuildShop_250814, 'guildshop_clean', 'GuildCoins', [800, 300, 2000, 60, 10, 20, 20, 400, 20, 40]),
        (GeneralShop_250814, 'general_clean', 'Coins', [2000, 5000, 2000, 1200, 360, 1500, 750, 10000, 900, 2000]),
    ):
        s = object.__new__(cls)
        s.config = shop.config
        im = load(folder / (frame + '.png'))
        if extract and cls in (GeneralShop_250814, CoreShop_250814):
            grid = s.shop_items()
            patches = ([((3, 0), 'BookYellowT2_4'), ((0, 1), 'PlateTorpedoT2_4'),
                        ((1, 1), 'PlateAntiAirT1_2'), ((3, 1), 'FoodT2_4')]
                       if cls is GeneralShop_250814 else [((0, 0), 'Chip_4')])
            for pos, name in patches:
                path = Path(s.shop_template_folder) / (name + '.png')
                icon = grid.item_class(im, grid.grids[pos]).image
                if path.exists():
                    assert np.array_equal(icon, load(path)), path
                else:
                    Image.fromarray(icon).save(str(path))
            del s.__dict__['shop_general_items' if cls is GeneralShop_250814 else 'shop_core_items']
        items = s.shop_detect_items(im)
        assert [v.price for v in items] == prices, frame
        assert all(v.cost == currency for v in items), frame
        if cls is GeneralShop_250814:
            assert [v.name for v in items] == (
                'BoxT3 BoxT4 BoxT3 BookYellowT2 BoxT2 PlateTorpedoT2 PlateAntiAirT1 BoxT3 FoodT2 BoxT3').split()
        if cls is CoreShop_250814:
            assert items[0].name == 'Chip'
    print('General, guild and core: 30/30 prices and currencies; general names: 10/10.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('folder', type=Path)
    p.add_argument('--extract', action='store_true')
    args = p.parse_args()
    run(args.folder, args.extract)
