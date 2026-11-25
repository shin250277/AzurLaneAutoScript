"""Replay five KR shops without purchasing; optional extraction saves labelled icons only."""
import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
from dev_tools.kr_protected_menu_replay import load
from module.config import server


def run(folder, extract=False):
    server.set_server('kr')
    if extract:
        rows = []
        for frame, cells in [('coremonthly_clean', [0, 2, 6]), ('guildshop_clean', [5, 9])]:
            im = load(folder / (frame + '.png'))
            for cell in cells:
                x, y = 265 + 169 * (cell % 5), 238 + 223 * (cell // 5)
                rows.append(im[y+115:y+155, x-12:x+85])
        strip = np.concatenate(rows, axis=0)
        fp = Path('dev_tools/fixtures/kr_shop_price_strips.png')
        if fp.exists():
            assert np.array_equal(load(fp), strip)
        else:
            Image.fromarray(strip).save(str(fp))
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
            s.config.CoreShop_Filter = 'Chip'
            s._currency = 34
            assert s.shop_get_item_to_buy(items) is None
            s._currency = 35
            assert s.shop_get_item_to_buy(items) is items[0]
        if cls is GeneralShop_250814:
            s.config.GeneralShop_Filter = 'FoodT2'
            s.config.GeneralShop_UseGems = False
            s.config.GeneralShop_ConsumeCoins = False
            s.config.GeneralShop_BuySkinBox = False
            s._currency = 900
            assert s.shop_get_item_to_buy(items) is items[8]
            items[8].cost = 'Gems'  # Mock a different price currency, not an account setting.
            assert s.shop_get_item_to_buy(items) is None
    print('General, guild and core: 30/30 prices and currencies; general names: 10/10.')
    from module.shop.shop_medal import MedalShop2_250814
    s = object.__new__(MedalShop2_250814)
    s.config = shop.config
    if extract:
        icon = load(folder / 'medal_clean.png')[589:608, 450:462]
        path = Path('assets/kr/shop/KR_MEDAL_PRICE_ICON.png')
        if path.exists():
            assert np.array_equal(load(path), icon)
        else:
            Image.fromarray(icon).save(str(path))
    for name in ('medal_clean', 'medal'):
        s.device = SimpleNamespace(image=load(folder / (name + '.png')))
        assert len(s._get_medals()) == 2
        items = s.shop_detect_items()
        assert [i.price for i in items] == [80, 80, 80, 30, 6, 10, 60, 30, 30, 30]
        assert all(i.cost == 'Medal' for i in items)
    from module.shop.shop_medal import KR_MEDAL_PRICE_ICON
    for name in ('coremonthly_clean', 'guildshop_clean', 'merit_clean', 'general_clean'):
        area = load(folder / (name + '.png'))[317:635, 265:999]
        assert not KR_MEDAL_PRICE_ICON.match_multi(area, similarity=0.83, threshold=5), name
    print('Medal: both rows and all 10 prices on both captures.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('folder', type=Path)
    p.add_argument('--extract', action='store_true')
    args = p.parse_args()
    run(args.folder, args.extract)
