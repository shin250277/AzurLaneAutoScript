"""KR's September 2026 preparation button beside the Handover tab."""
from module.base.button import Button

KR_MAP_PREPARATION = Button(
    area=(980, 495, 1096, 526), color=(250, 229, 163),
    button=(1015, 497, 1055, 527),
    file='./assets/kr/map/KR_MAP_PREPARATION.png', name='KR_MAP_PREPARATION')


def preparation_button(owner, interval=0):
    if owner.config.SERVER == 'kr' and owner.appear(
            KR_MAP_PREPARATION, offset=(80, 15), similarity=0.9, interval=interval):
        return KR_MAP_PREPARATION
    return None
