from collections import namedtuple
from datetime import datetime
import re

import cv2
from jellyfish import levenshtein_distance
import numpy as np
from yaml import safe_load

import module.config.server as server
from module.base.button import ButtonGrid
from module.base.decorator import cached_property, del_cached_property
from module.base.timer import Timer
from module.base.utils import color_similarity_2d, extract_letters, random_rectangle_vector_opted
from module.exception import GameTooManyClickError, RequestHumanTakeover
from module.island.data import DIC_ISLAND_ITEM, DIC_ISLAND_RECIPE, DIC_ISLAND_SHOP_ITEM_TO_RECIPE, DIC_ISLAND_SLOT
from module.island.utils import (
    ceil_div_or_ceil,
    get_idle_accumulating_batch_count,
    get_stuck_season_order_requirements,
    get_target_stock_load_rate,
    get_production_target_stock,
    load_hard_floor_items,
    load_item_mapping,
    merge_task_target_stuck_order_items,
    normalize_item_keys,
    parse_item_need_deadlines,
)
from module.island_handler.assets import *
from module.island_handler.exchange import IslandExchange
from module.island_handler.restaurant_config import get_menu_reserve_items
from module.island_handler.shop import IslandShop
from module.logger import logger
from module.map_detection.utils import Points
from module.ocr.ocr import Digit, Duration, Ocr
from module.ui.page import page_island, page_island_manage, page_island_shop


class IslandProductionRestart(Exception):
    def __init__(self, item_id, success=True):
        self.item_id = item_id
        self.success = success


RECIPE_SIZE = (280, 134)
RECIPE_DELTA = (0, 149)
RECIPE_DETECT_AREA = (181, 55, 460, 668)
RECIPE_DRAG_AREA = (300, 55, 350, 668)
RECIPE_ANCHOR_AREA = (58, 97, 102, 115)
RECIPE_PRODUCT_NAME_AREA = (123, 23, 269, 46)
RECIPE_PRODUCT_STOCK_AREA = (212, 92, 275, 110)
if server.server == 'jp':
    lang = 'jp'
elif server.server == 'tw':
    lang = 'tw'
else:
    lang = 'cnocr'
RECIPE_PRODUCT_NAME_OCR = Ocr([], lang=lang, letter=(57, 59, 61), threshold=160, name='product_name_ocr')
if server.server == 'kr':
    from module.island_handler.korean_ocr import KoreanIslandNameOcr
    RECIPE_PRODUCT_NAME_OCR = KoreanIslandNameOcr([], name='product_name_ocr_kr')
RECIPE_PRODUCT_STOCK_OCR = Digit([], lang='cnocr', letter=(80, 80, 80), threshold=160, name='product_stock_ocr')
if server.server == 'kr':
    from module.island_handler.korean_stock import KoreanRecipeStockDigit
    RECIPE_PRODUCT_STOCK_OCR = KoreanRecipeStockDigit(
        [], lang='cnocr', letter=(80, 80, 80), threshold=160, name='product_stock_ocr')
ISLAND_RECIPE_AMOUNT_OCR = Digit(ISLAND_RECIPE_AMOUNT, letter=(50, 50, 57), name='recipe_amount_ocr')


class IslandReversedDigitCounter(Ocr):
    def __init__(self, buttons, lang='cnocr', letter=(255, 255, 255), sub_letter=None, 
                 threshold=128, sub_threshold=128, 
                 background_color=None,
                 alphabet='0123456789/IDSB()+', name=None):
        super().__init__(buttons, lang=lang, letter=letter, threshold=threshold, alphabet=alphabet, name=name)
        self.sub_letter = sub_letter
        self.sub_threshold = sub_threshold
        self.background_color = background_color

    def pre_process(self, image):
        if self.background_color is not None:
            mask = color_similarity_2d(image, self.background_color)
            mask[mask < self.threshold] = 0
            line = cv2.bitwise_and(mask[0], mask[-1]).flatten()
            indices = np.where(line > 200)[0]
            left = indices[0] if len(indices) > 0 else 0
            right = indices[-1] + 1 if len(indices) > 0 else len(line)
            image = image[:, left:right]

        main_image = extract_letters(image, letter=self.letter, threshold=self.threshold)
        if self.sub_letter is not None and isinstance(self.sub_letter, tuple):
            mask = color_similarity_2d(image, self.sub_letter)
            mask[mask < self.sub_threshold] = 0
            if cv2.countNonZero(mask) > 30:
                sub_image = extract_letters(image, letter=self.sub_letter, threshold=self.sub_threshold)
                cv2.bitwise_and(main_image, sub_image, dst=main_image)

        main_image = cv2.copyMakeBorder(main_image, 2, 4, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
                    
        return main_image

    def after_process(self, result):
        result = super().after_process(result)
        result = result.replace('I', '1').replace('D', '0').replace('S', '5')
        result = result.replace('B', '8')
        if re.fullmatch(r'[0-9]+/?', result):
            normalized = f'{result.rstrip("/")}/0'
            logger.warning(f'Unexpected ocr result: {result}, normalized to {normalized}')
            result = normalized
        # Accept only "total/current" or "total/(current+bonus)". The last
        # capture handles a direct current value; the middle two are summed.
        match = re.fullmatch(r'([0-9]+)/(?:\(([0-9]+)\+([0-9]+)\)|([0-9]+))', result)
        if not match:
            logger.warning(f'Unexpected ocr result: {result}')
            return 0, 0, 0

        total = int(match.group(1))
        if match.group(4) is not None:
            current = int(match.group(4))
            components = (current, 0)
        else:
            current = int(match.group(2)) + int(match.group(3))
            components = (int(match.group(2)), int(match.group(3)))
        if hasattr(self, 'observed_components'):
            self.observed_components.append(components)
        return total, current, total - current


RECIPE_INGREDIENT_COUNTER_OCR = IslandReversedDigitCounter(
    [], lang='cnocr', letter=(255, 255, 255), sub_letter=(253, 171, 34),
    threshold=160, sub_threshold=160, background_color=(80, 80, 80), name='ingredient_counter_ocr'
)


def get_recipe_product_id(recipe_id):
    return next(iter(DIC_ISLAND_RECIPE[recipe_id]['commission_product']))


# demand is always the parsed [(count, period), ...] list from parse_item_need_deadlines.
# daily_buffer is the merged LP + manual buffer width contained in target_stock.
RecipeInfo = namedtuple('RecipeInfo', [
    'stock', 'target_stock', 'daily_buffer', 'batch_size', 'demand', 'idle_accumulating',
])


def get_target_stock_weight(stock, target_stock, daily_buffer):
    if stock >= target_stock or target_stock <= 0:
        return 0
    # Daily buffer is the consumable range above the floors, so its fill level
    # represents replenishment urgency. Fall back to the complete target for
    # manually configured floors that have no daily buffer.
    denominator = daily_buffer if daily_buffer > 0 else target_stock
    return (target_stock - stock) / denominator


def get_target_stock_replenish_workload(stock, target_stock, batch_size, workload):
    if stock >= target_stock:
        return 0
    delta_batch = ceil_div_or_ceil(target_stock - stock, batch_size)
    return delta_batch * workload


def get_demand_weight(stock, target_stock, batch_size, demand):
    rate_per_day = get_target_stock_load_rate(stock, target_stock, demand)
    if rate_per_day <= 0:
        return 0
    return rate_per_day / batch_size


def get_idle_accumulating_weight(stock, target_stock, demand, idle_accumulating):
    if idle_accumulating <= 0:
        return float('inf')
    demand_stock = demand[-1][0] if demand else 0
    effective_stock = max(stock - target_stock - demand_stock, 0)
    return effective_stock / idle_accumulating


RECIPE_MODE_BUFFER_SURPLUS = 'buffer_surplus'
RECIPE_MODE_IDLE_ACCUMULATING = 'idle_accumulating'


def get_recipe_entry_weight(recipe_id, info):
    workload = DIC_ISLAND_RECIPE[recipe_id]['workload']
    return (
        get_demand_weight(info.stock, info.target_stock, info.batch_size, info.demand),
        get_target_stock_weight(info.stock, info.target_stock, info.daily_buffer),
        -get_target_stock_replenish_workload(
            info.stock, info.target_stock, info.batch_size, workload
        ),
        -info.stock
    )


def get_optional_recipe_entry_weight(entry):
    recipe_id, info, mode = entry
    # Leading 0/1 keeps all buffer_surplus entries ahead of idle_accumulating
    # ones in the combined ascending sort.
    if mode == RECIPE_MODE_BUFFER_SURPLUS:
        return (
            0,
            info.stock / max(info.target_stock, info.batch_size, 1),
            DIC_ISLAND_RECIPE[recipe_id]['workload'],
            info.stock,
        )
    return (
        1,
        get_idle_accumulating_weight(info.stock, info.target_stock, info.demand, info.idle_accumulating),
        info.stock,
    )


class KoreanRecipeNameUnknown(RequestHumanTakeover):
    """Read-only name recognition failed; never authorize a production start."""


def recipe_product_name_to_recipe_id(name, slotcode=None):
    if server.server == 'jp':
        # While we have 果樹園二重奏 and 朝光活力コンビ, the problem of カニ as 力二 is worse,
        # so we replace 力 with カ before matching,
        # which can fix most of the misrecognition without causing new issues.
        name = name.replace('二', 'ニ').replace('力', 'カ')
    min_distance = float('inf')
    min_real_distance = float('inf')
    corrected_name = None
    corrected_id = None
    if isinstance(slotcode, int):
        recipe_lists = DIC_ISLAND_SLOT[slotcode]['formula'] + DIC_ISLAND_SLOT[slotcode]['activity_formula']
    else:
        recipe_lists = DIC_ISLAND_RECIPE.keys()

    if server.server == 'kr':
        normalized = re.sub(r'\s+', '', name or '')
        matches = [recipe_id for recipe_id in recipe_lists if normalized and normalized ==
                   re.sub(r'\s+', '', DIC_ISLAND_ITEM[get_recipe_product_id(recipe_id)]['name'].get('kr', ''))]
        if len(matches) == 1:
            return matches[0]
        logger.warning('KR recipe name is empty, unknown or ambiguous; do not guess a product')
        return None

    for recipe_id in recipe_lists:
        product_id = get_recipe_product_id(recipe_id)
        product_name = DIC_ISLAND_ITEM[product_id]['name'][server.server]

        # If product_name is longer than OCR result name, try matching any substring
        # of product_name with the same length as name and take the minimal distance.
        if isinstance(name, str) and isinstance(product_name, str) and len(product_name) >= len(name) and len(name) > 0:
            best_sub_distance = float('inf')
            L = len(name)
            for i in range(len(product_name) - L + 1):
                sub = product_name[i:i+L]
                d = levenshtein_distance(name, sub)
                if d < best_sub_distance:
                    best_sub_distance = d
            distance = best_sub_distance
            real_distance = levenshtein_distance(name, product_name)
        else:
            distance = levenshtein_distance(name, product_name)
            real_distance = distance
        if distance < min_distance or (distance == min_distance and real_distance < min_real_distance):
            min_distance = distance
            min_real_distance = real_distance
            corrected_name = product_name
            corrected_id = recipe_id

    if name != corrected_name:
        logger.info(f'Recipe product name OCR result "{name}" corrected to "{corrected_name}" with distance {min_distance} and real distance {min_real_distance}')
    return corrected_id


class IslandRecipe(IslandExchange, IslandShop):
    working_slot_id = None

    # recipe related methods
    def is_in_recipe_menu(self):
        return self.appear(ISLAND_RECIPE_CHECK, offset=(20, 20))

    def _get_recipe_buttons(self):
        area = (RECIPE_DETECT_AREA[0] + RECIPE_ANCHOR_AREA[0],
                RECIPE_DETECT_AREA[1] + RECIPE_ANCHOR_AREA[1],
                RECIPE_DETECT_AREA[2] - RECIPE_SIZE[0] + RECIPE_ANCHOR_AREA[2],
                RECIPE_DETECT_AREA[3] - RECIPE_SIZE[1] + RECIPE_ANCHOR_AREA[3])
        image = self.image_crop(area, copy=True)
        anchors = TEMPLATE_ISLAND_RECIPE_ANCHOR.match_multi(image, similarity=0.5, threshold=5)
        logger.attr('Recipe_in_view', len(anchors))
        rows = Points([(0., a.area[1]) for a in anchors]).group(threshold=5)
        return rows

    @cached_property
    def recipe_grid(self):
        for _ in self.loop(timeout=2):
            grid = self.get_recipe_grid()
            if (len(grid.buttons) >= 3 or getattr(grid, 'kr_scrollable', False)
                    or len(grid.buttons) == 1 and self.working_slot_id in [9031, 9032, 9033, 9034]):
                return grid
        return grid

    def get_recipe_grid(self):
        rows = self._get_recipe_buttons()
        count = len(rows)
        delta_y = RECIPE_DELTA[1]
        slot = DIC_ISLAND_SLOT.get(getattr(self, 'working_slot_id', None), {})
        if (server.server == 'kr' and slot.get('place') == 102
                and len(slot.get('formula', []) + slot.get('activity_formula', [])) == 1
                and count > 1):
            # The empty ranch panel can resemble the weak recipe anchor.
            # Only discard off-grid hits when the known single recipe has
            # its normal top anchor; never infer an unobserved first row.
            ys = sorted(rows[:, 1])
            top = 114 - RECIPE_DETECT_AREA[1]
            if abs(ys[0] - top) <= 3 and all(
                    abs((y - ys[0]) / delta_y - round((y - ys[0]) / delta_y)) * delta_y > 5
                    for y in ys[1:]):
                logger.info('Ignore off-grid empty-panel anchors for single KR ranch recipe')
                rows = rows[:1]
                count = 1
        if count > 4:
            logger.warning(f'Found {count} recipe anchors, which is more than expected, fixing count to 4')
            count = 4
        if count >= 2:
            y_list = rows[:, 1]
            y1, y2 = y_list[0], y_list[-1]
            origin_y = min(y1, y2) + RECIPE_DETECT_AREA[1]
        else:
            logger.warning('Unable to find enough recipe anchors, assume recipes are at top')
            origin_y = 114

        raw_count = count
        if server.server == 'kr' and count > 1 and origin_y + RECIPE_PRODUCT_NAME_AREA[1] < 110:
            # The fixed translucent header overprints a scrolled first name.
            # Read/select only unobscured rows; a later scroll exposes the
            # skipped product normally. Apply the same grid to names/stocks.
            origin_y += delta_y
            count -= 1
        recipe_grid = ButtonGrid(
            origin=(181, origin_y), delta=(0, delta_y), button_shape=RECIPE_SIZE,
            grid_shape=(1, count), name='RECIPE_GRID'
        )
        recipe_grid.kr_scrollable = server.server == 'kr' and raw_count >= 3
        return recipe_grid

    @cached_property
    def recipe_ids(self):
        return self.get_recipe_ids()

    def get_recipe_ids(self):
        # KR Hangul/underline can touch the 23px crop after anchor rounding.
        # Retain surrounding pixels for OCR/template context, not new click
        # or stock coordinates. Other servers keep their original crop.
        name_area = (123, 19, 269, 50) if server.server == 'kr' else RECIPE_PRODUCT_NAME_AREA
        product_name_grid = self.recipe_grid.crop(name_area, name='RECIPE_PRODUCT_NAME_GRID')
        product_name_images = [self.image_crop(button.area, copy=True) for button in product_name_grid.buttons]
        product_names = RECIPE_PRODUCT_NAME_OCR.ocr(product_name_images, direct_ocr=True)
        corrected_ids = [recipe_product_name_to_recipe_id(name, slotcode=self.working_slot_id) for name in product_names]
        if server.server == 'kr' and (not corrected_ids or None in corrected_ids):
            # Translucent labels/scrolling long text can be caught between
            # rasterization frames. Retry observations only, never clicks or
            # name correction. Require unchanged row geometry, no conflicting
            # known identity and two consecutive complete matching reads.
            areas = [tuple(button.area) for button in product_name_grid.buttons]
            known = list(corrected_ids)
            previous_complete = None
            for _ in range(3):
                self.device.sleep(.35)
                self.device.screenshot()
                if not self.is_in_recipe_menu():
                    break
                fresh_recipe_grid = self.get_recipe_grid()
                fresh_grid = fresh_recipe_grid.crop(name_area, name='RECIPE_PRODUCT_NAME_GRID')
                if [tuple(button.area) for button in fresh_grid.buttons] != areas:
                    break
                frames = [self.image_crop(button.area, copy=True) for button in fresh_grid.buttons]
                names = RECIPE_PRODUCT_NAME_OCR.ocr(frames, direct_ocr=True)
                ids = [recipe_product_name_to_recipe_id(name, slotcode=self.working_slot_id) for name in names]
                if None in ids and self.working_slot_id in DIC_ISLAND_SLOT:
                    from module.island_handler.korean_recipe_icon import resolve_recipe_icons
                    icon_grid = fresh_recipe_grid.crop((20, 20, 115, 115), name='KR_RECIPE_ICON_GRID')
                    icons = [self.image_crop(button.area, copy=True) for button in icon_grid.buttons]
                    confirmed = resolve_recipe_icons(names, ids, icons, self.working_slot_id)
                    if confirmed != ids:
                        logger.info('KR recipe icon and visible long text agree: %s' % confirmed)
                    ids = confirmed
                if len(ids) != len(known) or any(a is not None and b is not None and a != b
                                                for a, b in zip(known, ids)):
                    break
                known = [a if a is not None else b for a, b in zip(known, ids)]
                if ids and None not in ids and len(set(ids)) == len(ids):
                    if ids == previous_complete:
                        logger.info('KR recipe names recovered by two stable read-only captures')
                        return ids
                    previous_complete = ids
                else:
                    previous_complete = None
            self.device.image_save('./log/kr_island_recipe_unknown.png')
            raise KoreanRecipeNameUnknown('Korean recipe names are not all uniquely recognized; no production started')
        return corrected_ids

    def get_recipe_product_stocks(self):
        # KR scroll rounding can remove the bottom context of repeated digits
        # (observed 1311 -> 131). Preserve the original top/left prefix geometry.
        stock_area = (212, 92, 275, 114) if server.server == 'kr' else RECIPE_PRODUCT_STOCK_AREA
        stock_grid = self.recipe_grid.crop(stock_area, name='RECIPE_PRODUCT_STOCK_GRID')
        stock_images = [self.image_crop(button.area, copy=True) for button in stock_grid.buttons]
        stocks = RECIPE_PRODUCT_STOCK_OCR.ocr(stock_images, direct_ocr=True)
        return stocks

    def settle_korean_recipe_grid(self):
        """Wait for three row geometries within two pixels; never add input."""
        observations = []
        for _ in range(6):
            if not self.is_in_recipe_menu():
                raise RequestHumanTakeover('KR recipe page changed while waiting for scroll')
            grid = self.get_recipe_grid()
            areas = [tuple(button.area) for button in grid.buttons]
            logger.attr('KR recipe row geometry', areas)
            observations.append(areas)
            observations = observations[-3:]
            stable = (len(observations) == 3 and areas
                      and all(len(old) == len(areas) for old in observations))
            if stable:
                for rows in zip(*observations):
                    if (len({(r[0], r[2]) for r in rows}) != 1
                            or any(max(r[i] for r in rows)-min(r[i] for r in rows) > 2
                                   for i in (1, 3))):
                        stable = False
                        break
            if stable:
                # Names and stocks must use this same settled observation.
                self.recipe_grid = grid
                return
            self.device.sleep(.25)
            self.device.screenshot()
        self.device.image_save('./log/kr_island_recipe_unsettled.png')
        raise RequestHumanTakeover('KR recipe rows did not settle; no reading or production')

    def next_recipe_page(self):
        if len(self.recipe_grid.buttons) < 3 and not getattr(self.recipe_grid, 'kr_scrollable', False):
            logger.info('Less than 3 recipes in current page, no need to swipe to next page')
            return
        else:
            p1, p2 = random_rectangle_vector_opted((0, -300), box=RECIPE_DRAG_AREA, padding=0)
            self.device.drag(p1, p2, hold_duration=0.1, name='RECIPE_NEXT_PAGE_SWIPE')
            del_cached_property(self, 'recipe_grid')
            del_cached_property(self, 'recipe_ids')
            self.device.screenshot()

            if server.server == 'kr':
                self.settle_korean_recipe_grid()

    def prev_recipe_page(self):
        if len(self.recipe_grid.buttons) < 3 and not getattr(self.recipe_grid, 'kr_scrollable', False):
            logger.info('Less than 3 recipes in current page, no need to swipe to previous page')
            return
        else:
            p1, p2 = random_rectangle_vector_opted((0, 300), box=RECIPE_DRAG_AREA, padding=0)
            self.device.drag(p1, p2, hold_duration=0.1, name='RECIPE_PREV_PAGE_SWIPE')
            del_cached_property(self, 'recipe_grid')
            del_cached_property(self, 'recipe_ids')
            self.device.screenshot()
            if server.server == 'kr':
                self.settle_korean_recipe_grid()

    def scan_all_recipe_stocks(self):
        for _ in self.loop(timeout=3):
            # use ISLAND_RECIPE_AMOUNT_MAX as a check to ensure the recipe page is fully loaded
            if self.appear(ISLAND_RECIPE_AMOUNT_MAX, offset=(0, 20)):
                break
        all_stocks = {}
        drag_count = 0
        ISLAND_RECIPE_DRAG_CHECK.load_color(self.device.image)
        for _ in self.loop(timeout=30):
            recipe_ids = self.recipe_ids
            stocks = self.get_recipe_product_stocks()
            if server.server == 'kr':
                from module.island.kr_preflight import verified_recipe_stocks
                new_stocks = verified_recipe_stocks(recipe_ids, stocks, all_stocks)
                if new_stocks is None:
                    self.device.image_save('./log/kr_island_stock_unknown.png')
                    raise RequestHumanTakeover('KR recipe stock evidence incomplete or conflicting; no spending')
                # Keep the preceding accepted page locally so an overlap
                # mismatch has both observations, not only the second one.
                self.device.image_save('./log/kr_island_stock_previous.png')
            else:
                new_stocks = dict(zip(recipe_ids, stocks))
            all_stocks.update(new_stocks)
            self.next_recipe_page()
            drag_count += 1
            if self.appear(ISLAND_RECIPE_DRAG_CHECK, offset=(20, 20)):
                if drag_count > 1:
                    logger.info(f'Ensured recipe page bottom after dragging {drag_count} times')
                    self.device.click_record_clear()
                    break
            else:
                drag_count = 0
                ISLAND_RECIPE_DRAG_CHECK.load_color(self.device.image)
        else:
            if server.server == 'kr':
                self.device.image_save('./log/kr_island_stock_unknown.png')
                raise RequestHumanTakeover('KR recipe list bottom not confirmed; inventory scan incomplete')
        return all_stocks

    @cached_property
    def all_recipe_stocks(self):
        return self.scan_all_recipe_stocks()

    @cached_property
    def recipe_id_sequence(self):
        return self.get_recipe_id_sequence_to_run()

    @cached_property
    def hard_floor_items(self):
        yaml_text = self.config.cross_get("IslandProduction.IslandProduction.HardFloorItems", "")
        return normalize_item_keys(load_hard_floor_items(yaml_text))

    @cached_property
    def reserve_items(self):
        return get_menu_reserve_items(self.config)

    def get_task_target_items(self, task_target_items=None):
        if task_target_items is None:
            task_target_items = load_item_mapping(
                self.config.cross_get("IslandSeasonTask.IslandSeasonTask.TaskTarget", "{}"),
                config_name='TaskTarget',
            )
        stuck_season_order_id = self.config.cross_get(
            "IslandOrder.IslandOrder.StuckSeasonOrderId", 0
        )
        return merge_task_target_stuck_order_items(
            task_target_items,
            get_stuck_season_order_requirements(stuck_season_order_id),
        )

    def get_recipe_id_sequence_to_run(
            self,
            daily_buffer_items_dict=None,
            hard_floor_items_dict=None,
            reserve_items_dict=None,
            idle_accumulating_items_dict=None,
            task_target_items_dict=None,
    ):
        stocks_dict = self.all_recipe_stocks
        if daily_buffer_items_dict is None:
            yaml_text = self.config.cross_get("IslandProduction.IslandProduction.DailyBufferItems", "")
            if yaml_text is None:
                yaml_text = ""
            daily_buffer_items_dict = safe_load(yaml_text) or {}
        daily_buffer_items_dict = normalize_item_keys(daily_buffer_items_dict)
        # User-maintained supplement for items the LP plan leaves unbuffered,
        # merged by max so regular orders keep a consumable band above the floors.
        manual_buffer_items_dict = normalize_item_keys(safe_load(
            self.config.cross_get("IslandProduction.IslandProduction.ManualBufferItems", "") or ""
        ) or {})
        for item_id, amount in manual_buffer_items_dict.items():
            if amount > daily_buffer_items_dict.get(item_id, 0):
                daily_buffer_items_dict[item_id] = amount
        if hard_floor_items_dict is None:
            hard_floor_items_dict = self.hard_floor_items
        else:
            hard_floor_items_dict = normalize_item_keys(hard_floor_items_dict)
        if reserve_items_dict is None:
            reserve_items_dict = self.reserve_items
        else:
            reserve_items_dict = normalize_item_keys(reserve_items_dict)
        task_target_items_dict = self.get_task_target_items(task_target_items_dict)
        self.task_target_items = task_target_items_dict
        if idle_accumulating_items_dict is None:
            yaml_text = self.config.cross_get("IslandProduction.IslandProduction.IdleAccumulatingItems", "")
            if yaml_text is None:
                yaml_text = ""
            idle_accumulating_items_dict = safe_load(yaml_text) or {}
        idle_accumulating_items_dict = normalize_item_keys(idle_accumulating_items_dict)

        self.production_floor_items = hard_floor_items_dict, reserve_items_dict, daily_buffer_items_dict
        self.recipe_info_by_id = {}
        for recipe_id, stock in stocks_dict.items():
            recipe_product = DIC_ISLAND_RECIPE[recipe_id]['commission_product']
            product_id = get_recipe_product_id(recipe_id)
            batch_size = recipe_product[product_id]
            daily_buffer_width = daily_buffer_items_dict.get(product_id, 0)
            hard_floor = hard_floor_items_dict.get(product_id, 0)
            reserve = reserve_items_dict.get(product_id, 0)
            target_stock = get_production_target_stock(
                hard_floor,
                reserve,
                daily_buffer_width,
            )
            demand = task_target_items_dict.get(product_id, {})
            demand = parse_item_need_deadlines(demand)
            demand_text = ', '.join(
                f'{count} items in {period:g} days'
                for count, period in demand
            ) or '0 items in 1 days'
            idle_accumulating = idle_accumulating_items_dict.get(product_id, 0)
            info = RecipeInfo(stock, target_stock, daily_buffer_width, batch_size, demand, idle_accumulating)
            self.recipe_info_by_id[recipe_id] = info
            logger.info(
                f'Recipe {recipe_id} stock: {stock}, '
                f'daily_buffer_width: {daily_buffer_width}, '
                f'hard_floor: {hard_floor}, '
                f'reserve: {reserve}, '
                f'target_stock: {target_stock}, '
                f'batch_size: {batch_size}, task_target: {demand_text}, '
                f'idle accumulating rate: {idle_accumulating}'
            )
        self.checked_recipe_modes = set()
        return self._build_recipe_id_sequence_to_run()

    def _build_recipe_id_sequence_to_run(self):
        checked_modes = self.checked_recipe_modes
        normal_entries = []
        optional_entries = []
        run_counts = {
            recipe_id: self.calculate_recipe_run_count(info)
            for recipe_id, info in self.recipe_info_by_id.items()
        }
        # Products with unmet normal demand are protected: optional modes must not
        # consume them as ingredients, but may consume anything else (e.g. shop-bought
        # raw materials) above its protected stock, so slots don't idle needlessly.
        pending_products = {
            get_recipe_product_id(recipe_id)
            for recipe_id, count in run_counts.items() if count > 0
        }

        for recipe_id, info in self.recipe_info_by_id.items():
            recipe_cost = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
            if run_counts[recipe_id] > 0:
                if (recipe_id, None) not in checked_modes:
                    normal_entries.append((recipe_id, info, None))
            elif pending_products.intersection(recipe_cost):
                continue
            # Buffer surplus only converts coin-buyable shop materials (seeds,
            # feed, fry, flour) into tier-1 products. Surplus of recipe products
            # stays as-is: it is fungible for orders and downstream demand is
            # already maintained by normal replenishment.
            elif recipe_cost and all(item in DIC_ISLAND_SHOP_ITEM_TO_RECIPE for item in recipe_cost) \
                    and self.calculate_buffer_surplus_run_count(info) > 0 and (
                    recipe_id, RECIPE_MODE_BUFFER_SURPLUS
            ) not in checked_modes:
                optional_entries.append((recipe_id, info, RECIPE_MODE_BUFFER_SURPLUS))
            elif info.idle_accumulating > 0 and (
                    recipe_id, RECIPE_MODE_IDLE_ACCUMULATING
            ) not in checked_modes:
                # Reached for buffer_surplus recipes only after that mode failed
                # and was checked, via the rebuild in run().
                optional_entries.append((recipe_id, info, RECIPE_MODE_IDLE_ACCUMULATING))

        normal_entries.sort(key=lambda entry: get_recipe_entry_weight(entry[0], entry[1]), reverse=True)
        optional_entries.sort(key=get_optional_recipe_entry_weight)
        sequence = normal_entries + optional_entries
        logger.info(
            'Calculated recipe sequence to run: '
            f'{[(recipe_id, mode) for recipe_id, _info, mode in sequence]}'
        )
        return sequence

    @staticmethod
    def calculate_recipe_run_count(info):
        rate_per_day = get_target_stock_load_rate(info.stock, info.target_stock, info.demand)
        if rate_per_day > 0:
            return ceil_div_or_ceil(rate_per_day, info.batch_size)
        if info.stock < info.target_stock:
            return ceil_div_or_ceil(info.target_stock - info.stock, info.batch_size)
        return 0

    @staticmethod
    def calculate_buffer_surplus_run_count(info):
        # Surplus production is capped at one extra buffer width above the
        # target, so ingredient surplus is not endlessly converted into stock.
        headroom = info.target_stock + info.daily_buffer - info.stock
        if headroom <= 0:
            return 0
        return ceil_div_or_ceil(headroom, info.batch_size)

    def get_active_recipe_id(self):
        for recipe_id, button in zip(self.recipe_ids, self.recipe_grid.buttons):
            if self.is_button_selected(button):
                product_id = get_recipe_product_id(recipe_id)
                product_name = DIC_ISLAND_ITEM[product_id]['name'][server.server]
                logger.info(f'Selected recipe id: {recipe_id}, product name: {product_name}')
                return recipe_id
        logger.warning('Unable to determine selected recipe, assume no active recipe')
        return None

    def get_recipe_ingredient_grids(self, recipe_id=None):
        if recipe_id is None:
            recipe_id = self.get_active_recipe_id()
        if recipe_id is None:
            return None

        recipe_cost = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
        count = len(recipe_cost)
        logger.attr('Ingredient_count', count)
        if count == 0:
            return ButtonGrid(
                origin=(750, 474), delta=(0, 0), button_shape=(82, 83), grid_shape=(0, 1), name='RECIPE_INGREDIENT_GRID'
            )
        elif count == 1:
            return ButtonGrid(
                origin=(750, 474), delta=(0, 0), button_shape=(82, 83), grid_shape=(1, 1), name='RECIPE_INGREDIENT_GRID'
            )
        elif count == 2:
            return ButtonGrid(
                origin=(663, 474), delta=(175, 0), button_shape=(82, 83), grid_shape=(2, 1), name='RECIPE_INGREDIENT_GRID'
            )
        elif count == 3:
            return ButtonGrid(
                origin=(634, 474), delta=(116, 0), button_shape=(82, 83), grid_shape=(3, 1), name='RECIPE_INGREDIENT_GRID'
            )
        else:
            logger.warning(f'Unexpected ingredient count {count}, unable to determine ingredient grid')
            return None

    def get_recipe_ingredient_counters(self):
        self.recipe_ingredient_components = None
        active_recipe_id = self.get_active_recipe_id()
        ingredient_grids = self.get_recipe_ingredient_grids(active_recipe_id)
        if ingredient_grids is None:
            return None

        counter_grids = ingredient_grids.crop((-10, 66, 92, 84), name='counter_grids')
        for _ in self.loop(timeout=3):
            counter_images = [self.image_crop(button.area, copy=True) for button in counter_grids.buttons]
            RECIPE_INGREDIENT_COUNTER_OCR.observed_components = []
            counters = RECIPE_INGREDIENT_COUNTER_OCR.ocr(counter_images, direct_ocr=True)
            self.recipe_ingredient_components = list(RECIPE_INGREDIENT_COUNTER_OCR.observed_components)
            if (0, 0, 0) not in counters:
                break
        return counters

    def set_recipe(self, recipe_id):
        all_recipe_ids = list(self.all_recipe_stocks.keys())
        clicked = False
        for _ in self.loop(timeout=30):
            if clicked and self.get_active_recipe_id() == recipe_id:
                self.device.click_record_clear()
                return True
            if recipe_id in self.recipe_ids:
                index = self.recipe_ids.index(recipe_id)
                button = self.recipe_grid.buttons[index]
                self.device.click(button)
                clicked = True
                continue
            first_index = None
            for first_recipe_id in self.recipe_ids:
                if first_recipe_id in all_recipe_ids:
                    # Avoid error due to unscanned recipe_ids outside all_recipe_ids
                    first_index = all_recipe_ids.index(first_recipe_id)
                    break
            if first_index is None:
                logger.warning('No recognized recipe id in current page, swipe and retry')
                self.next_recipe_page()
                clicked = False
                continue
            if all_recipe_ids.index(recipe_id) < first_index:
                self.prev_recipe_page()
            else:
                self.next_recipe_page()
            clicked = False
        else:
            logger.warning(f'Unable to find recipe id {recipe_id} after looping through recipe pages, failed to set recipe')
            self.device.click_record_clear()
            return False

    def goto_ingredient_shop_page(self, entrance_button):
        click_timer = Timer(1, count=3).reset()
        for _ in self.loop(timeout=15):
            if self.appear(ISLAND_INFO_GOTO_SHOP, offset=(20, 20)):
                break
            if self.is_in_recipe_menu():
                if click_timer.reached_and_reset():
                    self.device.click(entrance_button)
        else:
            logger.warning('Unable to find ingredient button, failed to goto ingredient shop page')
            return False
        for _ in self.loop(timeout=15, skip_first=False):
            if self.appear_then_click(ISLAND_INFO_GOTO_SHOP, offset=(20, 20), interval=2):
                continue
            if self._island_shop_side_navbar.get_info(main=self)[0] == 0:
                return True
        else:
            logger.warning('Unable to find shop page in ingredient info page, failed to goto ingredient shop page')
            return False

    def prepare_ingredients(self, recipe_id, batch_count=float('inf'), mode=None):
        if self.config.SERVER == 'kr':
            # Never enter the foreign-server purchasing/exchange branches.
            # The selected recipe and a one-batch display must agree first.
            from module.island.kr_preflight import owned_batch_limit, verified_owned_unit_cost
            self.kr_owned_cost = None
            self.kr_owned_protected = None
            if (self.get_active_recipe_id() != recipe_id
                    or ISLAND_RECIPE_AMOUNT_OCR.ocr(self.device.image) != 1):
                return False, 0
            floors, reserves, buffers = self.production_floor_items
            tasks = self.get_task_target_items()
            cost = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
            protected = {}
            for item in cost:
                values = (floors.get(item, 0), reserves.get(item, 0), buffers.get(item, 0),
                          tasks.get(item, {}).get('total_need_count', 0))
                from numbers import Integral
                if any(isinstance(v, bool) or not isinstance(v, Integral) or v < 0 for v in values):
                    return False, 0
                protected[item] = sum(values)
            counters = self.get_recipe_ingredient_counters()
            # Only ranch formulas have the observed base+surcharge display.
            parts = (getattr(self, 'recipe_ingredient_components', None)
                     if recipe_id in (101013, 101015, 101016, 101018) else None)
            actual_cost = verified_owned_unit_cost(cost, counters, parts)
            if actual_cost is None:
                return False, 0
            count = owned_batch_limit(actual_cost, counters,
                                      batch_count, DIC_ISLAND_RECIPE[recipe_id]['production_limit'],
                                      protected)
            self.kr_owned_cost = (recipe_id, actual_cost)
            self.kr_owned_protected = protected
            return count == batch_count and count > 0, count
        # use this before setting recipe batch count to read out current ingredient need per batch,
        # since ranch recipes may have boosted ingredient requirement for higher batch production.
        counters = self.get_recipe_ingredient_counters()
        recipe_cost = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
        task_target_items = getattr(self, 'task_target_items', None)
        if task_target_items is None:
            task_target_items = self.get_task_target_items()
        hard_floor_items, reserve_items, daily_buffer_items = self.production_floor_items
        buffer_surplus_mode = mode == RECIPE_MODE_BUFFER_SURPLUS

        def get_available_stock(ingredient_key, stock):
            hard_floor = hard_floor_items.get(ingredient_key, 0)
            reserve = reserve_items.get(ingredient_key, 0)
            task_target = task_target_items.get(ingredient_key, {}).get('total_need_count', 0)
            if buffer_surplus_mode:
                protected_stock = get_production_target_stock(
                    hard_floor,
                    reserve,
                    daily_buffer_items.get(ingredient_key, 0),
                )
            else:
                protected_stock = max(hard_floor, 0) + max(reserve, 0)
            available_stock = max(stock - protected_stock - max(task_target, 0), 0)
            return available_stock, protected_stock, task_target

        if counters is None:
            logger.warning(f'Unable to read ingredient counters for recipe {recipe_id}')
            return False, 0
        if batch_count == float('inf'):
            max_count = DIC_ISLAND_RECIPE[recipe_id]['production_limit']
            for ingredient_key, counter in zip(recipe_cost, counters):
                if not buffer_surplus_mode and (
                        ingredient_key in DIC_ISLAND_SHOP_ITEM_TO_RECIPE
                        or ingredient_key in (2521, 2522)
                ):
                    continue
                available_stock, _protected_stock, _task_target = get_available_stock(
                    ingredient_key,
                    counter[0],
                )
                count = available_stock // counter[1] if counter[1] > 0 else float('inf')
                if count < max_count:
                    max_count = count
            batch_count = max_count
            logger.info(f'Calculated max batch count to produce with current ingredient stock: {batch_count}')
        success = True
        real_count = batch_count
        failed_buy_items = getattr(self, 'failed_buy_items', set())
        ingredient_grid = self.get_recipe_ingredient_grids(recipe_id)
        if ingredient_grid is None:
            logger.warning(f'Unable to determine ingredient grid for recipe {recipe_id}')
            return False, 0
        ingredient_buttons = ingredient_grid.buttons
        for ingredient_key, counter, button in zip(recipe_cost, counters, ingredient_buttons):
            available_stock, protected_stock, task_target_reserve = get_available_stock(
                ingredient_key,
                counter[0],
            )
            # Entering this branch implies counter[1] > 0, so divisions below are safe.
            if available_stock < real_count * counter[1]:
                if buffer_surplus_mode:
                    logger.info(
                        f'Ingredient {ingredient_key} has insufficient stock above protected stock '
                        f'{protected_stock} and task target {task_target_reserve}; '
                        'buffer surplus production will not buy or exchange ingredients'
                    )
                    real_count = min(real_count, available_stock // counter[1])
                    success = False
                    continue
                if ingredient_key in (2521, 2522):
                    if ingredient_key in failed_buy_items:
                        logger.warning(
                            f'Skipping exchange of ingredient {ingredient_key} after a previous failed exchange'
                        )
                        real_count = min(real_count, available_stock // counter[1])
                        success = False
                        continue
                    delta = real_count * counter[1] - available_stock
                    self.ui_back(check_button=page_island_manage.check_button)
                    self.ui_goto_island_shop()
                    exchange_success = super().island_shop_exchange({ingredient_key: delta})
                    # Exchange leaves the recipe menu. Return to production management and
                    # restart so the next attempt rescans recipe stocks and ingredient state.
                    self.ui_back(check_button=page_island.check_button)
                    self.ui_goto(page_island_manage)
                    raise IslandProductionRestart(item_id=ingredient_key, success=exchange_success)
                if ingredient_key in DIC_ISLAND_SHOP_ITEM_TO_RECIPE:
                    if ingredient_key in failed_buy_items:
                        logger.warning(
                            f'Skipping purchase of ingredient {ingredient_key} after a previous failed buy'
                        )
                        real_count = min(real_count, available_stock // counter[1])
                        success = False
                        continue
                    if ingredient_key == 3004:  # flour cannot be bought via jumping page, need to go to shop page to buy
                        self.ui_back(check_button=page_island_manage.check_button)
                        self.ui_goto_island_shop()
                        isolated = False
                    else:
                        self.goto_ingredient_shop_page(entrance_button=button)
                        isolated = True
                    delta = real_count * counter[1] - available_stock
                    buy_success = super().island_shop_buy({ingredient_key: delta}, isolated=isolated)
                    success = buy_success and success
                    if not isolated:
                        # We need an exception for inherited class to handle ui switch
                        # and restart the ingredient preparation after buying flour,
                        # since flour purchase requires going into shop page and back,
                        # which may cause the recipe page to lose the set recipe and ingredient states.
                        self.ui_back(check_button=page_island.check_button)
                        self.ui_goto(page_island_manage)
                        raise IslandProductionRestart(item_id=ingredient_key, success=buy_success)
                    else:
                        self.ui_back(check_button=self.is_in_recipe_menu)
                    if not success:
                        logger.warning(f'Failed to buy ingredient {ingredient_key} from shop, insufficient ingredient for recipe production')
                        real_count = min(real_count, available_stock // counter[1])
                else:
                    logger.warning(
                        f'Ingredient {ingredient_key} cannot be bought from shop, '
                        f'insufficient ingredient for recipe production after protected stock {protected_stock} '
                        f'and task target {task_target_reserve}'
                    )
                    real_count = min(real_count, available_stock // counter[1])
                    success = False
        return success, real_count

    def set_recipe_batch_count(self, batch_count=float('inf')):
        if self.config.SERVER == 'kr':
            from numbers import Integral
            if isinstance(batch_count, bool) or not isinstance(batch_count, Integral) or batch_count <= 0:
                return False
            # Do not jump to MAX or issue a blind multi-click sequence on KR.
            for _ in self.loop(skip_first=False, timeout=30):
                if not self.is_in_recipe_menu():
                    return False
                current = ISLAND_RECIPE_AMOUNT_OCR.ocr(self.device.image)
                if isinstance(current, bool) or not isinstance(current, Integral) or current <= 0:
                    return False
                if current == batch_count:
                    return True
                button = ISLAND_RECIPE_AMOUNT_PLUS if current < batch_count else ISLAND_RECIPE_AMOUNT_MINUS
                self.appear_then_click(button, offset=(20, 20), interval=0.3)
            return False
        for _ in self.loop():
            if self.appear_then_click(ISLAND_RECIPE_AMOUNT_MAX, offset=(20, 20)):
                self.device.screenshot()
                break
        if batch_count == float('inf'):
            logger.info('Set recipe amount to max')
            return True
        else:
            logger.info(f'Set recipe amount to {batch_count}')
            if ISLAND_RECIPE_AMOUNT_OCR.ocr(self.device.image) < batch_count:
                # Check if already at max, if so, cannot set to desired amount
                counters = self.get_recipe_ingredient_counters()
                for counter in counters:
                    if counter[2] < 0:
                        logger.warning('Insufficient ingredient for next recipe amount, cannot set recipe amount to desired value')
                        return False
            try:
                self.ui_ensure_index(index=batch_count, letter=ISLAND_RECIPE_AMOUNT_OCR,
                                 next_button=ISLAND_RECIPE_AMOUNT_PLUS,
                                 prev_button=ISLAND_RECIPE_AMOUNT_MINUS,)
                return True
            except GameTooManyClickError:
                logger.warning('Too many clicks when setting recipe amount, failed to set recipe amount')
                return False

    def get_recipe_remain_time(self):
        if self.match_template_color(ISLAND_RECIPE_TIME_ANCHOR, offset=(100, 20)):
            ISLAND_RECIPE_TIME.load_offset(ISLAND_RECIPE_TIME_ANCHOR)
            remain_time = Duration(ISLAND_RECIPE_TIME.button, lang='cnocr', name='recipe_remain_time').ocr(self.device.image)
            return remain_time
        else:
            logger.warning('Unable to find recipe time anchor, failed to execute recipe')
            return None

    def run_recipe(self, recipe_id, batch_count=float('inf'), mode=None):
        """
        Returns:
            tuple[timedelta, int | float]: remain time and actual batch count after starting,
                or None if failed to start recipe
        """
        self.last_unavailable_product = None
        if not self.is_in_recipe_menu():
            logger.warning('Not in recipe menu, cannot run recipe')
            return None
        if not self.set_recipe(recipe_id):
            logger.warning(f'Failed to set recipe to {recipe_id}, cannot run recipe')
            return None
        if self.config.SERVER == 'kr' and not self.set_recipe_batch_count(1):
            logger.warning('KR one-batch baseline could not be verified; no ingredient planning or start')
            return None
        success, real_count = self.prepare_ingredients(
            recipe_id,
            batch_count=batch_count,
            mode=mode,
        )
        if real_count <= 0:
            logger.warning('No batch can be produced with current ingredient stock, cannot run recipe')
            self.last_unavailable_product = get_recipe_product_id(recipe_id)
            return None
        if not success:
            logger.warning(f'Failed to prepare enough ingredient for {batch_count} batch(es) production')
            logger.info(f'Can only produce {real_count} batch(es) with current ingredient stock, will try to run with this amount')
        if not self.set_recipe_batch_count(real_count):
            logger.warning(f'Failed to set recipe batch count to {"max" if real_count == float("inf") else real_count}, cannot run recipe')
            return None
        remain_time = self.get_recipe_remain_time()
        logger.attr('Recipe_remain_time', remain_time)
        if remain_time is not None:
            if self.config.SERVER == 'kr':
                from module.island.kr_preflight import owned_start_verified, validate_recipe_counters
                from module.exception import RequestHumanTakeover
                # Do not use the repeating foreign-server start-click loop.
                self.device.screenshot()
                protected = getattr(self, 'kr_owned_protected', None)
                evidence = getattr(self, 'kr_owned_cost', None)
                counters = self.get_recipe_ingredient_counters()
                declared = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
                parts = (getattr(self, 'recipe_ingredient_components', None)
                         if recipe_id in (101013, 101015, 101016, 101018) else None)
                if (protected is None or self.get_active_recipe_id() != recipe_id
                        or evidence is None or evidence[0] != recipe_id
                        or ISLAND_RECIPE_AMOUNT_OCR.ocr(self.device.image) != real_count
                        or remain_time.total_seconds() <= 0
                        or (declared and not validate_recipe_counters(
                            declared, real_count, counters, require_available=False, components=parts))
                        or not owned_start_verified(
                            evidence[1], counters, real_count, protected)):
                    raise RequestHumanTakeover('KR final production evidence changed; no start')
                self.device.click(ISLAND_RECIPE_TIME_ANCHOR)
                for _ in self.loop(timeout=15):
                    if self.match_template_color(page_island_manage.check_button, offset=(0, 20)):
                        self.kr_last_consumption = (recipe_id, real_count,
                            {item: counter[1] for item, counter in zip(evidence[1], counters)})
                        logger.info(f'KR owned recipe {recipe_id} started once, amount {real_count}')
                        return remain_time, real_count
                raise RequestHumanTakeover('KR production start outcome uncertain; no repeated start click')
            for _ in self.loop():
                if self.appear_then_click(ISLAND_RECIPE_TIME_ANCHOR, offset=(100, 20), interval=2):
                    continue
                if not self.is_in_recipe_menu():
                    break
            logger.info(f'Recipe {recipe_id} started with amount {"max" if real_count == float("inf") else real_count}, remain time: {remain_time}')
            return remain_time, real_count
        else:
            logger.warning('Failed to get recipe remain time, recipe may not have started successfully')
            return None

    def update_recipe_id_sequence_and_stock(self, recipe_id, batch_count):
        recipe_cost = DIC_ISLAND_RECIPE[recipe_id]['commission_cost']
        consumed_items = {item_id: amount * batch_count for item_id, amount in recipe_cost.items()}
        if self.config.SERVER == 'kr':
            evidence = getattr(self, 'kr_last_consumption', None)
            if evidence is None or evidence[:2] != (recipe_id, batch_count):
                raise RequestHumanTakeover('KR production consumption evidence missing')
            consumed_items = evidence[2]
            self.kr_last_consumption = None
        for old_recipe_id, info in self.recipe_info_by_id.items():
            product_id = get_recipe_product_id(old_recipe_id)
            if old_recipe_id == recipe_id:
                new_stock = info.stock + info.batch_size * batch_count
                logger.info(
                    f'Updated recipe {recipe_id} stock from {info.stock} to {new_stock} '
                    f'after running recipe for {batch_count} batch(es)'
                )
            elif product_id in consumed_items:
                new_stock = info.stock - consumed_items[product_id]
                logger.info(
                    f'Updated recipe {old_recipe_id} stock from {info.stock} to {new_stock} '
                    f'after consuming {consumed_items[product_id]} item(s) for recipe {recipe_id}'
                )
            else:
                continue
            self.recipe_info_by_id[old_recipe_id] = info._replace(stock=new_stock)
            self.all_recipe_stocks[old_recipe_id] = new_stock
        self.recipe_id_sequence = self._build_recipe_id_sequence_to_run()

    def run(self, slot_id=None):
        """
        Returns:
            target_time (datetime): timestamp of when the recipe will finish, or None if failed to run any recipe
        """
        self.working_slot_id = slot_id
        del_cached_property(self, 'recipe_grid')
        del_cached_property(self, 'recipe_ids')
        while self.recipe_id_sequence:
            recipe_id, info, mode = self.recipe_id_sequence[0]
            production_limit = DIC_ISLAND_RECIPE[recipe_id]['production_limit']
            if mode == RECIPE_MODE_BUFFER_SURPLUS:
                batch_count = self.calculate_buffer_surplus_run_count(info)
            elif mode:
                batch_count = get_idle_accumulating_batch_count(
                    DIC_ISLAND_RECIPE[recipe_id]['workload'],
                    self.config.ISLAND_IDLE_ACCUMULATING_DISPATCH_HOURS,
                )
            else:
                batch_count = self.calculate_recipe_run_count(info)
            strategy = mode or 'normal'
            logger.info(
                f'Plan to run {batch_count} batch(es) of recipe {recipe_id} in {strategy} mode, '
                f'limitation: {production_limit} batches'
            )
            if batch_count > production_limit:
                logger.info(f"Will try to run {production_limit} batches")
                batch_count = production_limit
            result = self.run_recipe(recipe_id, batch_count, mode=mode)
            if result is not None:
                remain_time, real_count = result
                target_time = datetime.now() + remain_time
                logger.info(
                    f'Will run recipe {recipe_id} in {strategy} mode for {real_count} batch(es), '
                    f'expected target time: {target_time}'
                )
                self.update_recipe_id_sequence_and_stock(recipe_id, real_count)
                return target_time
            else:
                unavailable_product = getattr(self, 'last_unavailable_product', None)
                if unavailable_product is not None:
                    logger.info(
                        f'Product {unavailable_product} is unavailable after recipe {recipe_id} failed'
                    )
                self.checked_recipe_modes.add((recipe_id, mode))
                self.recipe_id_sequence = self._build_recipe_id_sequence_to_run()
        logger.info('No recipe to run or failed to run any recipe')
        return None
