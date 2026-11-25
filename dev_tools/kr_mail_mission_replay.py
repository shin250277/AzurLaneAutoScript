"""Check KR recognition on local screenshots, without input or account access."""
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image
from module.config import server


def run(root):
    server.set_server('kr')
    from module.freebies.mail_white import MailWhite, MAIL_MANAGE, MAIL_BATCH_CLAIM, MAIL_BATCH_DELETE
    from module.freebies import assets as mail_assets
    from module.reward.reward import Reward
    mail, mission = object.__new__(MailWhite), object.__new__(Reward)
    mission.device = mail.device = SimpleNamespace(stuck_record_add=lambda button: None)
    mission.config = mail.config = SimpleNamespace(SERVER='kr')
    for name in ('all', 'storage', 'collection', 'manage', 'special'):
        with Image.open(str(root / ('mail_' + name + '.jpg'))) as im:
            mail.device.image = np.array(im.convert('RGB'))
        for button, expected in ((MAIL_MANAGE, 'all'), (MAIL_BATCH_CLAIM, 'manage'),
                                 (MAIL_BATCH_DELETE, 'manage')):
            assert mail.appear(button, offset=(30, 30)) == (name == expected), (name, button)
        if name == 'manage':
            for option in ('ALL', 'CUBE', 'COINS', 'OIL', 'MERIT', 'GEMS'):
                button = getattr(mail_assets, 'MAIL_SELECT_' + option)
                assert mail.mail_select_setting.is_option_active(button) == (option == 'ALL'), option
    for tab in ('all', 'main', 'side', 'daily', 'weekly', 'event'):
        with Image.open(str(root / ('mission_' + tab + '.jpg'))) as im:
            mission.device.image = np.array(im.convert('RGB'))
        expected = {'event': 'MISSION_EMPTY', 'weekly': 'KR_MISSION_SINGLE'}.get(tab, 'KR_MISSION_UNFINISH')
        assert str(mission._reward_get_state()) == expected, tab
    print('Mail buttons 15/15, mail checkbox states 6/6, mission states 6/6 passed')


if __name__ == '__main__':
    run(Path(sys.argv[1]))
