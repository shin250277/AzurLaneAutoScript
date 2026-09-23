"""Claim once from the visually verified Bigshot personal rewards dialog."""
from module.base.button import Button
from module.exception import RequestHumanTakeover

HEADER = Button(area=(390, 135, 515, 166), color=(0, 0, 0),
                button=(390, 135, 515, 166),
                file='./assets/kr/raid/BIGSHOT_REWARDS_HEADER.png')
CLAIM = Button(area=(794, 576, 852, 603), color=(124, 162, 209),
               button=(794, 576, 852, 603),
               file='./assets/kr/raid/BIGSHOT_REWARDS_CLAIM.png')


def claim_visible_rewards(ui):
    if ui.config.SERVER != 'kr' or ui.config.Campaign_Event != 'raid_20260827':
        raise RequestHumanTakeover('Only the observed KR Bigshot event is supported')
    ui.device.screenshot()
    for index in range(12):
        if ui.handle_get_items():
            ui.device.sleep(1)
            ui.device.screenshot()
            continue
        if not ui.appear(HEADER, offset=(5, 5)):
            raise RequestHumanTakeover('Personal rewards dialog not recognized')
        if not CLAIM.match_template_color(ui.device.image, offset=(5, 5), threshold=30):
            ui.device.image_save('./log/kr_bigshot_rewards_claim_finished.png')
            return
        ui.device.click(CLAIM)
        ui.device.sleep(1)
        ui.device.screenshot()
        ui.device.image_save('./log/kr_bigshot_rewards_claim_%02d.png' % index)
    raise RequestHumanTakeover('Reward inspection reached bounded step limit')
