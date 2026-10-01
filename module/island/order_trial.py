"""Single KR iron-ore order; no buying, rejecting, speeding up or replanning."""
import json
from datetime import datetime
from pathlib import Path

RECEIPT = Path('log/kr_iron_order_trial_20261002_attempt.json')


def validate_requirements(requirements):
    if set(requirements) != {2703}:
        return False
    value = requirements[2703]
    return (len(value) == 3 and all(type(n) is int for n in value)
            and value[0] >= 6 and value[1] == 6 and value[2] == value[0] - 6)


def reserve_attempt(path, requirements):
    if not validate_requirements(requirements):
        raise ValueError('Only a single six-iron-ore order is allowed')
    with path.open('x', encoding='utf-8') as stream:
        json.dump({'item': 2703, 'maximum_cost': 6, 'requirements': requirements,
                   'attempted_at': datetime.now().isoformat()}, stream)


def run_trial(ui):
    from module.base.button import Button
    from module.exception import RequestHumanTakeover
    from module.logger import logger
    from module.ui.page import page_island_order
    if ui.config.SERVER != 'kr' or RECEIPT.exists():
        raise RequestHumanTakeover('KR single-order trial unavailable or already attempted')
    submit = Button(area=(1115, 639, 1169, 665), color=(87, 199, 255),
                    button=(1115, 639, 1169, 665), name='KR_IRON_ORDER_SUBMIT',
                    file='./assets/kr/island/KR_IRON_ORDER_SUBMIT.png')
    ui.ui_ensure(page_island_order)
    ui.detect_all_orders()
    for order in ui.regular_orders[:15]:
        x1, y1, x2, y2 = order.button
        if not (0 <= x1 < x2 < 800 and 150 <= y1 < y2 <= 650):
            continue
        ui.click_order(order)
        ui.device.screenshot()
        requirements = ui.scan_current_order_requirements()
        if not validate_requirements(requirements):
            continue
        # Keep existing stock reservations; no force/urgent override.
        if not ui.is_order_satisfied(requirements):
            continue
        ui.device.screenshot()
        if ui.scan_current_order_requirements() != requirements:
            raise RequestHumanTakeover('Order changed between observations')
        if not ui.match_template_color(submit, offset=(0, 0)):
            raise RequestHumanTakeover('Localized submit control is not visible')
        ui.device.image_save('./log/kr_iron_order_before.png')
        reserve_attempt(RECEIPT, requirements)
        ui.device.click(submit)
        # Never click the submit control again, even on an uncertain outcome.
        for _ in ui.loop(timeout=15, skip_first=False):
            if ui.handle_island_additional():
                continue
            if ui.handle_island_order_level_up():
                continue
        ui.device.image_save('./log/kr_iron_order_after.png')
        logger.info('One KR iron order submit attempted; inspect quota/reward/stock before declaring success')
        return
    raise RequestHumanTakeover('No eligible six-iron-ore order within existing stock protections')
