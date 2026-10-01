"""Conservative KR regular orders; no rejection, purchase or target changes."""
import re
from datetime import datetime

PENDING_KEY = 'IslandOrder.Storage.Storage.KoreanPendingSubmission'


def safe_order_target(order):
    from module.base.button import Button
    x1, y1, x2, y2 = order.button
    x, y = (x1 + x2) // 2, (y1 + y2) // 2
    # Spawned KR portraits can sit at (800, 80). Keep random clicks inside
    # the portrait center, below the header and left of the requirements pane.
    if not (0 <= x1 < x2 <= 855 and 0 <= y1 < y2 <= 650
            and 16 <= x <= 825 and 70 <= y <= 630):
        return None
    box = (x - 8, y - 8, x + 8, y + 8)
    return Button(area=box, color=(), button=box, name=str(order.name))


def parse_quota(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r'(\d{1,2})/15', value.strip())
    if match and 0 <= int(match.group(1)) <= 15:
        return int(match.group(1))
    return None


def read_quota(ui):
    from module.ocr.ocr import Ocr
    # Observed KR normal-order quota; reject malformed OCR instead of clamping.
    ocr = Ocr((950, 23, 1011, 47), lang='cnocr', letter=(255, 255, 255),
              threshold=128, alphabet='0123456789/', name='KR_ORDER_QUOTA')
    return parse_quota(ocr.ocr(ui.device.image))


def submit_regular(ui):
    from module.base.button import Button
    from module.exception import RequestHumanTakeover
    from module.logger import logger
    if ui.config.SERVER != 'kr' or ui.config.cross_get(PENDING_KEY, None):
        raise RequestHumanTakeover('KR order has an unresolved attempt or wrong server; do not retry')
    ui.device.screenshot()
    before = read_quota(ui)
    if before is None:
        raise RequestHumanTakeover('Cannot verify KR daily order quota')
    if before == 0:
        return False
    requirements = ui.scan_current_order_requirements()
    if not requirements or not ui.is_order_satisfied(requirements):
        return False
    ui.device.screenshot()
    if read_quota(ui) != before or ui.scan_current_order_requirements() != requirements:
        raise RequestHumanTakeover('KR order changed between observations')
    submit = Button(area=(1115, 639, 1169, 665), color=(87, 199, 255),
                    button=(1115, 639, 1169, 665), name='KR_REGULAR_ORDER_SUBMIT',
                    file='./assets/kr/island/KR_IRON_ORDER_SUBMIT.png')
    if not ui.match_template_color(submit, offset=(0, 0)):
        raise RequestHumanTakeover('KR regular submit control is not active')
    ui.device.image_save('./log/kr_regular_order_before.png')
    # Persist before dispatch so process interruption cannot automatically retry.
    ui.config.cross_set(PENDING_KEY, {'quota': before, 'requirements': requirements,
                                    'attempted_at': datetime.now().isoformat()})
    ui.config.update()
    ui.device.click(submit)
    confirmations = 0
    for _ in ui.loop(timeout=20, skip_first=False):
        if ui.handle_island_additional() or ui.handle_island_order_level_up():
            confirmations = 0
            continue
        after = read_quota(ui)
        confirmations = confirmations + 1 if after == before - 1 else 0
        if confirmations >= 2:
            ui.device.image_save('./log/kr_regular_order_after.png')
            ui.config.cross_set(PENDING_KEY, None)
            logger.info(f'KR regular order confirmed: quota {before} -> {after}')
            return True
    ui.device.image_save('./log/kr_regular_order_uncertain.png')
    raise RequestHumanTakeover('KR quota decrease was not confirmed; attempt remains blocked')


def run_regular_orders(ui):
    from module.exception import RequestHumanTakeover
    from module.logger import logger
    from module.ui.page import page_island_order
    if ui.config.cross_get(PENDING_KEY, None):
        raise RequestHumanTakeover('Unresolved KR order attempt; inspect before another submission')
    ui.ui_ensure(page_island_order)
    completed = 0
    for _ in range(15):
        ui.detect_all_orders()
        progressed = False
        for order in ui.regular_orders[:15]:
            target = safe_order_target(order)
            if target is None:
                continue
            ui.click_order(target)
            if submit_regular(ui):
                completed += 1
                progressed = True
                break
        if not progressed:
            break
    logger.info(f'KR regular orders completed: {completed}; urgent/season/rejection untouched')
    ui.config.task_delay(minute=30, server_update=True)
