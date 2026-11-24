"""Check archive entrances on private, locally captured KR cards, without input."""
import sys
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
from PIL import Image

from module.config import server


# (capture, left/right card top in native coordinates, expected runtime templates)
ROWS = [
    ('archive_list', 153, 'VISITORS_DYED_IN_RED WINTERS_CROWN'),
    ('archive_list', 451, 'DIVERGENT_CHESSBOARD FALLEN_WINGS'),
    ('ex_05_06', 414, 'IRIS_OF_LIGHT_AND_DARK INK_STAINED_STEEL_SAKURA'),
    ('ex_07_10', 162, 'CRIMSON_ECHOES SCHERZO_OF_IRON_AND_BLOOD'),
    ('ex_07_10', 459, 'EMPYREAL_TRAGICOMEDY ASHEN_SIMULACRUM'),
    ('ex_11_14', 204, 'SWIRLING_CHERRY_BLOSSOMS MICROLAYER_MEDLEY'),
    ('ex_11_14', 501, 'SKYBOUND_ORATORIO NORTHERN_OVERTURE'),
    ('ex_15_18', 242, 'AURORA_NOCTIS INVERTED_ORTHANT'),
    ('ex_15_18', 539, 'DREAMWAKERS_BUTTERFLY MIRROR_INVOLUTION'),
    ('ex_19_22', 183, 'KHOROVOD_OF_DAWNS_RIME UPON_THE_SHIMMERING_BLUE'),
    ('ex_19_22', 481, 'DAEDALIAN_HYMN TOWER_OF_TRANSCENDENCE'),
    ('ex_23_26', 92, 'ABYSSAL_REFRAIN PLEDGE_OF_THE_RADIANT_COURT'),
    ('ex_23_26', 390, 'AQUILIFERS_BALLADE RONDO_AT_RAINBOWS_END'),
    ('ex27_28', 223, 'VIOLET_TEMPEST_BLOOMING_LYCORIS PARALLEL_SUPERIMPOSITION'),
    ('ex_27_30', 239, 'REVELATIONS_OF_DUST CONFLUENCE_OF_NOTHINGNESS'),
    ('ex_27_30', 536, '- -'),
    ('sp1', 153, 'STRIVE_WISH_AND_STRATEGIZE ENCIRCLING_GRAF_SPEE'),
    ('sp1', 451, 'GLORIOUS_BATTLE PRELUDE_UNDER_THE_MOON'),
    ('sp5', 354, 'CRESCENDO_OF_POLARIS THE_SOLOMON_RANGER'),
    ('sp_recheck', 373, 'THE_ENIGMA_AND_THE_SHARK UNIVERSE_IN_UNISON'),
    ('sp9', 345, 'STARS_OF_THE_SHIMMERING_FJORD THE_WAY_HOME_IN_THE_NIGHT'),
    ('sp13', 74, 'COUNTERATTACK_WITHIN_THE_FJORD SUNDERED_BLUE'),
    ('sp13', 372, 'THE_FLAME_TOUCHED_DAGGER VIRTUAL_TOWER'),
    ('sp17', 70, 'TEMPESTA_AND_THE_FOUNTAIN_OF_YOUTH OPERATION_CONVERGENCE'),
    ('sp17', 367, 'ANTHEM_OF_REMEMBRANCE INTERLUDE_OF_ILLUSIONS'),
    ('sp_01', 182, '- -'),
    ('sp_01', 481, '- -'),
]


def main(directory):
    server.set_server('kr')
    from module.war_archives.dictionary import dic_archives_template
    from campaign.campaign_war_archives.campaign_base import CampaignBase
    replay = object.__new__(CampaignBase)
    replay.device = SimpleNamespace()
    folders = {t.name.replace('TEMPLATE_', '', 1): k for k, t in dic_archives_template.items()}
    templates = {t.name.replace('TEMPLATE_', '', 1): t for t in dic_archives_template.values()}
    expected = [k for _, _, names in ROWS for k in names.split() if k != '-']
    assert len(set(expected)) == len(expected) and set(expected) == set(templates)
    failures = []
    for file, top, names in ROWS:
        with Image.open(str(directory / (file + '.jpg'))) as im:
            image = np.array(im.convert('RGB'))
        replay.device.image = image
        for left, name in zip((95, 729), names.split()):
            card = image[max(107, top):min(top+172, 720), left:left+454]
            scores = {k: cv2.minMaxLoc(cv2.matchTemplate(card, t.image, cv2.TM_CCOEFF_NORMED))[1]
                      for k, t in templates.items() if all(a >= b for a, b in zip(card.shape, t.image.shape))}
            hits = {k for k, score in scores.items() if score >= 0.85}
            if hits != ({name} if name != '-' else set()):
                failures.append((file, name, round(scores.get(name, 0), 3), sorted(hits)))
            if name != '-':
                entry = replay._get_archives_entrance(folders[name])
                # Includes the clickable Files header and completion strip, not just the illustration.
                if entry is None or not (left-7 <= entry.button[0] < entry.button[2] <= left+464 and
                                         max(106, top-25) <= entry.button[1] < entry.button[3] <= top+219):
                    failures.append((file, name, 'entrance outside target card'))
    for file in ('home', 'sortie', 'universe_map'):
        with Image.open(str(directory / (file + '.jpg'))) as im:
            replay.device.image = np.array(im.convert('RGB'))
        for name, folder in folders.items():
            if replay._get_archives_entrance(folder) is not None:
                failures.append((file, name, 'unexpected entrance'))
    from module.war_archives.war_archives import DATA_KEY_CAMPAIGN, WAR_ARCHIVES_CAMPAIGN_CHECK
    assert WAR_ARCHIVES_CAMPAIGN_CHECK.match(replay.device.image, (20, 20))
    assert DATA_KEY_CAMPAIGN.ocr(replay.device.image) == (300, 0, 300)
    print('Supported: {}, card slots: {}, discrepancies: {}'.format(len(expected), 2*len(ROWS), failures))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1])))
