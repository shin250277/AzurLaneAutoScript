"""One explicitly approved KR potato batch. No purchasing or repeat clicks."""
import json
from datetime import datetime
from pathlib import Path


RECEIPT = Path('log/kr_potato_trial_20260915_attempt.json')


def validate_trial(active, amount, counters):
    return (active == 101007 and amount == 1 and len(counters or []) == 1
            and len(counters[0]) == 3 and counters[0][0] >= 9
            and counters[0][1] == 9 and counters[0][2] == counters[0][0] - 9)


def reserve_attempt(path=RECEIPT):
    # Exclusive create: an uncertain click must never consume a second batch.
    with path.open('x', encoding='utf-8') as stream:
        json.dump({'recipe': 101007, 'seed': 1005, 'maximum_seed_cost': 9,
                   'batches': 1, 'attempted_at': datetime.now().isoformat()}, stream)


def run_trial(ui):
    from module.exception import RequestHumanTakeover
    from module.island_handler.recipe import ISLAND_RECIPE_AMOUNT_OCR
    from module.island_handler.assets import ISLAND_RECIPE_TIME_ANCHOR
    from module.ui.page import page_island_manage
    from module.logger import logger
    if RECEIPT.exists():
        raise RequestHumanTakeover('Potato trial was already attempted; no automatic retry')
    if not ui.set_recipe(101007):
        raise RequestHumanTakeover('Could not select the approved potato recipe')
    ui.device.screenshot()
    # Do not call prepare_ingredients/run_recipe: those support purchasing.
    if not validate_trial(ui.get_active_recipe_id(), ISLAND_RECIPE_AMOUNT_OCR.ocr(ui.device.image),
                          ui.get_recipe_ingredient_counters()):
        ui.device.image_save('./log/kr_potato_trial_invalid.png')
        raise RequestHumanTakeover('Expected potato, one batch, and exactly nine existing seeds')
    duration = ui.get_recipe_remain_time()
    if duration is None or duration.total_seconds() <= 0:
        ui.device.image_save('./log/kr_potato_trial_start_unknown.png')
        raise RequestHumanTakeover('Production start/time could not be verified')
    ui.device.image_save('./log/kr_potato_trial_before.png')
    reserve_attempt()
    ui.device.click(ISLAND_RECIPE_TIME_ANCHOR)
    for _ in ui.loop(timeout=15):
        if ui.match_template_color(page_island_manage.check_button, offset=(0, 20)):
            ui.device.image_save('./log/kr_potato_trial_after.png')
            logger.info('KR potato trial: one start click, returned to management; verify slot before claiming success')
            raise RequestHumanTakeover('Single potato trial returned to management; no further production')
    ui.device.image_save('./log/kr_potato_trial_uncertain.png')
    raise RequestHumanTakeover('Potato start outcome uncertain; receipt prevents another click')


def inspect_trial(ui):
    """Only open the already-used first field slot; never confirm/cancel work."""
    from module.exception import RequestHumanTakeover
    from module.ui.page import page_island_manage
    if not ui.match_template_color(page_island_manage.check_button, offset=(0, 20)):
        raise RequestHumanTakeover('Inspect trial only from the production management page')
    grid = ui.slot_grids.get(101)
    if grid is None or ui.is_slot_empty(grid.buttons[0]):
        raise RequestHumanTakeover('Expected occupied first field slot is not visible')
    ui.device.click(grid.buttons[0])
    for _ in ui.loop(timeout=3):
        pass
    ui.device.image_save('./log/kr_potato_trial_running.png')
    raise RequestHumanTakeover('Existing potato slot opened for inspection; no new production or cancellation')
