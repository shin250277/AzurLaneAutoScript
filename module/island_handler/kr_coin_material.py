"""Observed KR ordinary-coin material dialog; no premium-currency fallback."""
from numbers import Integral


def material_shortfall(stock, unit, protected, batches):
    values = (stock, unit, protected, batches)
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v < 0 for v in values):
        return None
    if unit <= 0 or batches <= 0:
        return None
    missing = max(0, unit * batches + protected - stock)
    return missing if missing <= 100 else None


def purchase_allowed(cost, name, amount, price, expected_name, expected_amount, coin):
    if set(cost) != {1} or not coin:
        return False
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v <= 0
           for v in (cost[1], amount, price, expected_amount)):
        return False
    return (expected_amount <= 100 and amount == expected_amount
            and price == cost[1] * amount
            and isinstance(name, str) and bool(name.strip())
            and ''.join(name.split()) == ''.join(expected_name.split()))


AREAS = {'header': (299, 122, 347, 150), 'coin': (636, 559, 661, 582),
         'confirm': (907, 556, 950, 583), 'close': (971, 117, 1003, 149)}


def marker(image, name):
    from module.base.template import Template
    from module.base.utils import crop
    return Template('./assets/kr/island_material/%s.png' % name).match(
        crop(image, AREAS[name]), similarity=.96)


def read_quantity(image):
    """Require independent digit models to agree; never infer quantity from price."""
    from module.ocr.ocr import Digit
    values = [Digit([(756, 360, 850, 382)], lang=lang,
                    letter=(57, 58, 60), threshold=threshold,
                    name='kr_material_amount_' + lang).ocr(image)
              for lang, threshold in [('azur_lane', 80), ('cnocr', 128)]]
    return values[0] if values[0] == values[1] and 1 <= values[0] <= 100 else 0


def dialog_evidence(image):
    from module.island_handler.korean_ocr import KoreanIslandShopNameOcr
    from module.ocr.ocr import Digit
    if not all(marker(image, name) for name in ('header', 'coin', 'confirm', 'close')):
        return None
    name = KoreanIslandShopNameOcr([(623, 184, 987, 212)], name='kr_material_name').ocr(image)
    amount = read_quantity(image)
    price = Digit([(681, 558, 753, 583)], letter=(221, 221, 221),
                  name='kr_material_price').ocr(image)
    return name, amount, price


def buy_material(ui, item, amount, entrance):
    from module.base.button import Button
    from module.island.data import DIC_ISLAND_SHOP_ITEM_TO_RECIPE, DIC_ISLAND_SHOP_RECIPE
    from module.island_handler.assets import (ISLAND_SHOP_BUY_AMOUNT_PLUS_ONE,
        ISLAND_SHOP_BUY_AMOUNT_MINUS_ONE, ISLAND_SHOP_BUY_AMOUNT_PLUS_TEN,
        ISLAND_SHOP_BUY_AMOUNT_MINUS_TEN)
    from module.ui.page import page_island_shop
    from module.exception import RequestHumanTakeover
    from module.logger import logger
    target = DIC_ISLAND_SHOP_ITEM_TO_RECIPE.get(item)
    recipe = DIC_ISLAND_SHOP_RECIPE.get(target, {})
    cost = recipe.get('resource_consume', {})
    if (ui.config.SERVER != 'kr' or set(cost) != {1}
            or material_shortfall(0, 1, 0, amount) is None):
        return False
    if not ui.goto_ingredient_shop_page(entrance):
        raise RequestHumanTakeover('KR ingredient shop navigation failed; no purchase')
    balance = ui.island_shop_get_currency().get(1, 0)
    if balance < cost[1] * amount:
        ui.ui_back(check_button=ui.is_in_recipe_menu)
        return False
    ids = ui.island_shop_get_item_ids()
    if ids.count(target) != 1:
        raise RequestHumanTakeover('KR shop item not uniquely identified; no purchase')
    ui.device.click(ui._island_shop_item_grid.buttons[ids.index(target)])
    expected_name = recipe['name']['kr']
    for _ in ui.loop(timeout=30):
        evidence = dialog_evidence(ui.device.image)
        if evidence is None:
            continue
        name, current, price = evidence
        if not purchase_allowed(cost, name, current, price, expected_name, current, True):
            raise RequestHumanTakeover('KR purchase dialog identity or coin price mismatch')
        if current == amount:
            break
        diff = amount - current
        button = (ISLAND_SHOP_BUY_AMOUNT_PLUS_TEN if diff >= 10 else
                  ISLAND_SHOP_BUY_AMOUNT_MINUS_TEN if diff <= -10 else
                  ISLAND_SHOP_BUY_AMOUNT_PLUS_ONE if diff > 0 else ISLAND_SHOP_BUY_AMOUNT_MINUS_ONE)
        ui.device.click(button)
    else:
        raise RequestHumanTakeover('KR purchase quantity not confirmed; no purchase')
    # Fresh, independent evidence immediately before the single confirmation.
    ui.device.screenshot()
    evidence = dialog_evidence(ui.device.image)
    if evidence is None or not purchase_allowed(cost, *evidence, expected_name, amount, True):
        raise RequestHumanTakeover('KR final purchase evidence changed; no purchase')
    confirm = Button(area=AREAS['confirm'], color=(0, 0, 0),
                     button=AREAS['confirm'], name='KR_COIN_MATERIAL_BUY')
    ui.device.click(confirm)
    for _ in ui.loop(timeout=15):
        # Never re-click confirmation on uncertain result.
        if ui.ui_page_appear(page_island_shop) and not marker(ui.device.image, 'header'):
            after = ui.island_shop_get_currency().get(1)
            if after != balance - cost[1] * amount:
                raise RequestHumanTakeover('KR purchase balance change unverified; do not retry')
            logger.info('KR coin material purchase verified: item=%s amount=%s coins=%s',
                        item, amount, cost[1] * amount)
            ui.ui_back(check_button=ui.is_in_recipe_menu)
            return True
        ui.handle_island_additional()
    raise RequestHumanTakeover('KR purchase result uncertain; do not retry')


def replenish_for_recipe(ui, recipe_id, cost, counters, protected, batches, mode):
    from module.island.data import DIC_ISLAND_SHOP_ITEM_TO_RECIPE, DIC_ISLAND_SHOP_RECIPE
    from module.exception import RequestHumanTakeover
    # Material buying must never become recursive ingredient crafting.
    if len(cost) != 1 or mode == 'buffer_surplus':
        return counters
    item, unit = next(iter(cost.items()))
    shop = DIC_ISLAND_SHOP_RECIPE.get(DIC_ISLAND_SHOP_ITEM_TO_RECIPE.get(item), {})
    if set(shop.get('resource_consume', {})) != {1}:
        return counters
    missing = material_shortfall(counters[0][0], unit, protected.get(item, 0), batches)
    if not missing:
        return counters
    grid = ui.get_recipe_ingredient_grids(recipe_id)
    if grid is None or len(grid.buttons) != 1:
        return counters
    old_stock = counters[0][0]
    if not buy_material(ui, item, missing, grid.buttons[0]):
        return counters
    if not ui.set_recipe(recipe_id) or not ui.set_recipe_batch_count(1):
        raise RequestHumanTakeover('KR bought material but recipe could not be restored')
    ui.device.screenshot()
    fresh = ui.get_recipe_ingredient_counters()
    if (fresh is None or len(fresh) != 1 or fresh[0] !=
            (old_stock + missing, unit, old_stock + missing - unit)):
        raise RequestHumanTakeover('KR purchased material inventory change unverified; do not retry')
    return fresh


def recover_preview(ui):
    """Dismiss an observed purchase preview without confirming it."""
    from module.base.button import Button
    from module.ui.page import page_island_shop
    from module.exception import RequestHumanTakeover
    if not (marker(ui.device.image, 'header') and marker(ui.device.image, 'close')):
        return False
    ui.device.click(Button(area=AREAS['close'], color=(0, 0, 0),
                           button=AREAS['close'], name='KR_MATERIAL_PREVIEW_CLOSE'))
    for _ in ui.loop(timeout=10):
        if not marker(ui.device.image, 'header') and ui.ui_page_appear(page_island_shop):
            return True
    raise RequestHumanTakeover('KR purchase preview did not close; no purchase')
