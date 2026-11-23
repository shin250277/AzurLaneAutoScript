"""Replay KR submenu controls on local game frames; no emulator or game input."""
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
from PIL import Image
import module.config.server as server


def run(directory, current, dorm):
    server.set_server('kr')
    from module.exercise.exercise import NEW_OPPONENT, OCR_EXERCISE_REMAIN, OCR_PERIOD_REMAIN
    from module.war_archives.assets import WAR_ARCHIVES_EX_ON, WAR_ARCHIVES_SP_ON
    from module.gacha.assets import BUILD_SUBMIT_ORDERS, BUILD_SUBMIT_WW_ORDERS
    from module.gacha.assets import SHOP_MEDAL_CHECK, BUILD_FINISH_ORDERS
    from module.shop.assets import NAV_GENERAL, NAV_MONTHLY, TAB_GENERAL, TAB_MERIT
    from module.shop import assets as shop
    from module.commission.assets import COMMISSION_DAILY, COMMISSION_URGENT
    from module.gacha.gacha_reward import OCR_BUILD_COIN_COUNT, OCR_BUILD_CUBE_COUNT
    from module.dorm.dorm import DORM_FEED_CHECK, OCR_FILL, OCR_SLOT

    def frame(name, source=directory):
        with Image.open(str(source / (name + '.png'))) as im:
            assert im.size == (1280, 720)
            return np.array(im.convert('RGB'))

    for path in sorted(directory.glob('*.png')):
        assert NEW_OPPONENT.appear_on(frame(path.stem)) == (
            path.stem in ('exercise', 'exercise_again')), path.stem
    for name, duration in [('exercise', timedelta(days=7, hours=4, minutes=6, seconds=36)),
                           ('exercise_again', timedelta(days=7, hours=3, minutes=58))]:
        im = frame(name)
        assert OCR_EXERCISE_REMAIN.ocr(im) == 10
        assert OCR_PERIOD_REMAIN.ocr(im) == duration
    im = frame('archives')
    assert WAR_ARCHIVES_EX_ON.appear_on(im) and not WAR_ARCHIVES_SP_ON.appear_on(im)
    im = frame('build')
    assert BUILD_SUBMIT_ORDERS.appear_on(im) and not BUILD_SUBMIT_WW_ORDERS.appear_on(im)
    im = frame('munitionslive')
    assert all(b.match(im, (20, 20)) for b in (NAV_GENERAL, TAB_GENERAL))
    assert not any(b.match(im, (20, 20)) for b in (NAV_MONTHLY, TAB_MERIT))
    tabs = 'GENERAL MERIT GUILD META PRIZE CORE_LIMITED CORE_MONTHLY MEDAL PROTOTYPE'.split()
    names = ('general_clean merit_clean guildshop_clean metashop_clean prize_clean '
             'monthly coremonthly_clean medal_clean prototype_clean').split()
    for n, expected in zip(names, tabs):
        im = frame(n, current)
        assert [t for t in tabs if getattr(shop, 'TAB_'+t).match(im, (20, 20))] == [expected], n
    for buttons, names in [
        ((WAR_ARCHIVES_EX_ON, WAR_ARCHIVES_SP_ON), ('archiveex', 'spuncovered')),
        ((COMMISSION_DAILY, COMMISSION_URGENT), ('commdaily', 'urgentclean')),
    ]:
        for index, name in enumerate(names):
            im = frame(name, current)
            assert [b.appear_on(im) for b in buttons] == [index == 0, index == 1], name
    im = frame('exercise23', current)
    assert NEW_OPPONENT.appear_on(im) and OCR_EXERCISE_REMAIN.ocr(im) == 10
    assert OCR_PERIOD_REMAIN.ocr(im) == timedelta(days=6, hours=2, minutes=18, seconds=23)
    regular_build = {'build', 'build23', 'build2', 'buildlight', 'buildspecial', 'buildheavy'}
    for source in (directory, current):
        for p in source.glob('*.png'):
            im = frame(p.stem, source)
            assert BUILD_SUBMIT_ORDERS.appear_on(im) == (p.stem in regular_build), p.stem
            assert SHOP_MEDAL_CHECK.appear_on(im) == (p.stem in ('support23', 'support2')), p.stem
    assert BUILD_FINISH_ORDERS.appear_on(frame('queue23', current))
    for name in ('build23', 'buildlight', 'buildspecial'):
        im = frame(name, current)
        assert (OCR_BUILD_COIN_COUNT.ocr(im), OCR_BUILD_CUBE_COUNT.ocr(im)) == (23275, 1775)
    im = frame('dormfeed', dorm)
    assert DORM_FEED_CHECK.appear_on(im)
    assert OCR_FILL.ocr(im) == (0, 42000, 42000)
    assert OCR_SLOT.ocr(frame('dormok23', dorm)) == (6, 0, 6)
    print('KR exercise OCR and refresh, archive, build, commission, nine shop selectors: OK')


if __name__ == '__main__':
    run(*(Path(arg) for arg in sys.argv[1:]))
