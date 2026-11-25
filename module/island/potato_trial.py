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


def collect_trial(ui):
    """Collect the original completed first field slot, without dispatching."""
    from module.exception import RequestHumanTakeover
    from module.logger import logger
    if not RECEIPT.exists():
        raise RequestHumanTakeover('Original potato trial receipt is required')
    ui.ensure_island_production_page()
    ui.ensure_top_page()
    grid = ui.slot_grids.get(101)
    if grid is None or not grid.buttons:
        raise RequestHumanTakeover('Original first field slot is not visible')
    slot = grid.buttons[0]
    ui.device.screenshot()
    if not ui.is_slot_finished(slot):
        if ui.is_slot_empty(slot):
            return audit_trial_stock(ui, slot)
        raise RequestHumanTakeover('Original slot is not finished or was already collected; no action')
    ui.device.image_save('./log/kr_potato_trial_collection_before.png')
    if not ui.claim_slot_reward(slot):
        raise RequestHumanTakeover('Original slot reward collection was not confirmed')
    ui.device.screenshot()
    ui.device.image_save('./log/kr_potato_trial_collection_after.png')
    if ui.is_slot_finished(slot):
        raise RequestHumanTakeover('Original slot still has a reward; no dispatch or retry')
    logger.info('KR potato trial reward collected; no new production, purchase, or exchange')
    return True


def audit_trial_stock(ui, slot):
    """Read farm stock and potato seed balance from an empty slot, never start."""
    from module.exception import RequestHumanTakeover
    from module.island.assets import ISLAND_PRODUCTION_SELECT_CHARACTER
    from module.island.data import DIC_ISLAND_PRODUCTION_PLACE
    from module.ui.page import page_island_manage
    from module.logger import logger
    if not RECEIPT.exists() or not ui.is_slot_empty(slot):
        raise RequestHumanTakeover('Stock audit requires the original receipt and an empty first slot')
    for _ in ui.loop(timeout=15):
        if ui.is_in_island_dock():
            break
        if ui.appear_then_click(ISLAND_PRODUCTION_SELECT_CHARACTER, offset=(60, 20), interval=1):
            continue
        if ui.match_template_color(page_island_manage.check_button, interval=1) and not ui.is_enter_window_shown():
            ui.device.click(slot)
    if not ui.is_in_island_dock():
        raise RequestHumanTakeover('Could not open read-only stock selection')
    ui.island_dock_select_manjuu()
    ui.island_dock_select_confirm(ui.is_in_recipe_menu)
    ui.working_slot_id = DIC_ISLAND_PRODUCTION_PLACE[101]['slot'][0]
    stocks = ui.scan_all_recipe_stocks()
    logger.attr('KR potato post-collection stocks', stocks)
    if not ui.set_recipe(101007):
        raise RequestHumanTakeover('Potato stock selection was not recognized')
    counters = ui.get_recipe_ingredient_counters()
    logger.attr('KR potato post-collection seeds', counters)
    ui.device.image_save('./log/kr_potato_trial_stock_audit.png')
    # Close the recipe without pressing its production or material buttons.
    ui.ui_back(check_button=page_island_manage.check_button)
    logger.info('KR potato stock audit complete; recipe closed without starting work')
    return True


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
