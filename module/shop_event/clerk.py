import cv2
from pathlib import Path

from module.base.button import ButtonGrid
from module.base.decorator import cached_property
from module.base.timer import Timer
from module.base.utils import color_mask, crop, load_image
from module.combat.assets import GET_SHIP, GET_ITEMS_1, GET_ITEMS_3
from module.exception import RequestHumanTakeover
from module.logger import logger
from module.map_detection.utils import Points
from module.shop.assets import AMOUNT_PLUS, AMOUNT_MINUS, AMOUNT_MAX, SHOP_BUY_CONFIRM_AMOUNT, SHOP_BUY_CONFIRM, \
    SHOP_CLICK_SAFE_AREA
from module.shop.clerk import OCR_SHOP_AMOUNT
from module.shop_event.assets import *
from module.shop_event.item import ITEM_SHAPE, EventShopItemGrid, DELTA_PRICE_BACKGROUND, DELTA_ITEM, \
    PRICE_BACKGROUND_COLOR, PRICE_THRESHOLD
from module.shop_event.ui import EventShopUI, EVENT_SHOP_SCROLL
from module.ui_white.assets import BACK_ARROW_WHITE
from module.shop_event.korean_currency import validated_point_items

DETECT_AREA = (221, 194, 1049, 632)


class ItemNotFoundError(Exception):
    pass


def kr_sold_out_page(image, grid):
    """An empty prediction is skippable only if every detected card says sold out."""
    buttons = grid.buttons
    if not buttons or len(buttons) > 10:
        return False
    # The same badge is rerasterized at fractional scroll positions. Smooth
    # subpixel edges, while retaining the full checkmark + Korean text shape.
    templates = [cv2.GaussianBlur(load_image(str(path)), (3, 3), 0)
                 for path in Path('./assets/shop/event_kr_sold_out').glob('*.png')]
    if not templates:
        return False
    confirmed_cards = 0
    for button in buttons:
        x, y, right, bottom = button.area
        if x < DETECT_AREA[0] or right > DETECT_AREA[2] or y < DETECT_AREA[1] \
                or y + 149 > DETECT_AREA[3]:
            return False
        # The final row may contain fewer than five products. Grid cells over
        # background are not cards; require the actual dark price pill.
        pill = crop(image, (x - 20, y + 125, x + 85, y + 142))
        # Price digits occupy up to a third of this crop in observed cards.
        if cv2.countNonZero(color_mask(pill, PRICE_BACKGROUND_COLOR, threshold=25)) < pill.shape[0] * pill.shape[1] * 0.5:
            continue
        card = cv2.GaussianBlur(crop(image, button.area), (3, 3), 0)
        confirmed = False
        for template in templates:
            height, width = template.shape[:2]
            _, score, _, position = cv2.minMaxLoc(cv2.matchTemplate(card, template, cv2.TM_CCOEFF_NORMED))
            px, py = position
            actual = card[py:py + height, px:px + width]
            if score >= 0.97 and sum(cv2.mean(cv2.absdiff(actual, template))[:3]) / 3 <= 12:
                confirmed = True
                break
        if not confirmed:
            return False
        confirmed_cards += 1
    return confirmed_cards > 0


def merge_scan_page(items, previous_last_row, new_items):
    """Only compare adjacent observed rows, never historical screen coordinates."""
    if not new_items:
        raise ValueError('Empty event shop scan page')
    first_row = [item for item in new_items if item.button[1] == new_items[0].button[1]]
    last_row = [item for item in new_items if item.button[1] == new_items[-1].button[1]]

    def identity(item):
        return item.name, item.amount, item.price, item.cost, item.button[0]

    def same_visible_item(old, new):
        if identity(old) == identity(new):
            return True
        # Names can disagree after fractional-scroll rasterization. Compare
        # the adjacent actual icon as well; never merge by price alone.
        if identity(old)[1:] != identity(new)[1:]:
            return False
        if not hasattr(old, 'image') or not hasattr(new, 'image'):
            return False
        score = cv2.minMaxLoc(cv2.matchTemplate(
            old.image, new.image[4:41, 4:59], cv2.TM_CCOEFF_NORMED))[1]
        return score >= 0.93

    if previous_last_row and len(previous_last_row) == len(first_row) and all(
            same_visible_item(old, new) for old, new in zip(previous_last_row, first_row)):
        # Use the newer row: a settled screenshot may repair an invalid counter.
        return items[:-len(previous_last_row)] + new_items, last_row
    return items + new_items, last_row


class EventShopClerk(EventShopUI):
    pt_image = None
    urpt_image = None

    def _get_event_shop_grid(self):
        # PRICE_THRESHOLD is a color similarity, color_mask takes a color tolerance
        mask = color_mask(self.device.image, PRICE_BACKGROUND_COLOR, threshold=255 - PRICE_THRESHOLD)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=8)
        mask = crop(mask,
                    (DETECT_AREA[0], DETECT_AREA[1] + DELTA_PRICE_BACKGROUND[1], DETECT_AREA[2], DETECT_AREA[3]),
                    copy=False)
        buttons = TEMPLATE_COST_PRICE_BACKGROUND.match_multi(mask, similarity=0.6)
        points = Points([(0., p.area[1]) for p in buttons]).group(threshold=5)

        row = len(points)
        if row == 2:
            y = min(points[0][1], points[1][1]) + DETECT_AREA[1]
            delta_y = abs(points[0][1] - points[1][1])
        elif row == 1:
            y = points[0][1] + DETECT_AREA[1]
            delta_y = 215
        else:
            logger.warning(f"Unexpected number of rows: {row}, assuming scroll at top.")
            y = 1 + DETECT_AREA[1]  # Start position is 1 pixel lower than detect area
            delta_y = 215

        shop_grid = ButtonGrid(
            origin=(DETECT_AREA[0] + DELTA_ITEM[0], y + DELTA_ITEM[1]),
            delta=(169, delta_y),
            button_shape=ITEM_SHAPE,
            grid_shape=(5, row),
            name="EVENT_SHOP_GRID",
        )
        return shop_grid

    @cached_property
    def event_shop_items(self):
        event_shop_items = EventShopItemGrid(grids=None, templates={})
        event_shop_items.load_template_folder('./assets/shop/event')
        return event_shop_items

    def event_shop_get_items(self, scroll_pos=None):
        self.ensure_no_info_bar()
        for attempt in range(3):
            self.event_shop_items.grids = self._get_event_shop_grid()
            if self.config.SHOP_EXTRACT_TEMPLATE:
                self.event_shop_items.extract_template(self.device.image, './assets/shop/event')
            self.event_shop_items.predict(self.device.image, name=True, amount=True, cost=False,
                                          price=True, tag=True, counter=True, scroll_pos=scroll_pos)
            shop_items = self.event_shop_items.items
            # Invalid OCR uses 0/0; a valid sold-out counter is 0/N.
            invalid = [item for item in shop_items if item.count == 0 and item.total_count == 0]
            if not invalid:
                break
            if attempt >= 2:
                message = f'Invalid event shop counter after {attempt + 1} scans: {[str(item) for item in invalid]}'
                logger.error(message)
                raise ItemNotFoundError(message)
            logger.warning(f'Invalid event shop counter, retrying: {[str(item) for item in invalid]}')
            self.device.screenshot()

        if len(shop_items):
            min_row = self.event_shop_items.grids[0, 0].area[1]
            row = [str(item) for item in shop_items if item.button[1] == min_row]
            logger.info(f'Shop row 1: {row}')
            row = [str(item) for item in shop_items if item.button[1] != min_row]
            logger.info(f'Shop row 2: {row}')
            return shop_items
        else:
            logger.info('No shop items found')
            return []

    def scan_all(self):
        items = []
        previous_last_row = []
        self.device.click_record_clear()

        logger.hr('Event Shop Scan', level=2)
        EVENT_SHOP_SCROLL.set_top(main=self)
        # KR's clipped bottom row needs more overlap to avoid skipping products.
        stride = 0.4 if self.config.SERVER == 'kr' else 0.66
        for _ in range(40):
            new_items = self.event_shop_get_items(scroll_pos=EVENT_SHOP_SCROLL.cal_position(main=self))
            if not new_items:
                if self.config.SERVER != 'kr' or not kr_sold_out_page(
                        self.device.image, self.event_shop_items.grids):
                    raise RequestHumanTakeover('Empty event shop scan page; refuse incomplete inventory')
                logger.info('KR event shop: every visible full card is sold out; continue to actual bottom')
                previous_last_row = []
            else:
                items, previous_last_row = merge_scan_page(items, previous_last_row, new_items)
            if EVENT_SHOP_SCROLL.at_bottom(main=self):
                logger.info('Event shop reach bottom')
                break
            else:
                EVENT_SHOP_SCROLL.next_page(main=self, page=stride)
                continue
        else:
            raise RequestHumanTakeover('Event shop scan did not reach bottom; refuse incomplete inventory')
        return items

    def event_shop_buy_item(self, item_to_buy, amount=None):
        scroll_pos = item_to_buy.scroll_pos
        EVENT_SHOP_SCROLL.set(scroll_pos, main=self)
        items = self.event_shop_get_items()
        items = [item for item in items if item.name == item_to_buy.name
                 and item.count == item_to_buy.count and item.price == item_to_buy.price]
        if self.config.SERVER == 'kr':
            token = getattr(item_to_buy, 'kr_currency_token', None)
            items = [item for item in items
                     if item.amount == item_to_buy.amount and item.cost == item_to_buy.cost
                     and validated_point_items([item], token)]
        if len(items) == 0:
            logger.error(f'Item {item_to_buy} not found at scroll position {scroll_pos}')
            logger.warning(f'Will try to rerun the task.')
            raise ItemNotFoundError(f'Item {item_to_buy} not found at scroll position {scroll_pos}')
        elif len(items) > 1:
            logger.warning(f'Multiple items found for {item_to_buy} at scroll position {scroll_pos}, '
                           f'buying the first one')
        item = items[0]
        # For ship items, while it may have multiple stock, can only buy one at a time.
        if getattr(item, 'is_ship', False):
            buy_times = item.count if amount is None else min(amount, item.count)
            for _ in range(buy_times):
                self.event_shop_buy_item_execute(item, amount=1)
        else:
            self.event_shop_buy_item_execute(item, amount=amount)

    def event_shop_buy_item_execute(self, item, amount):
        if self.config.SERVER == 'kr' and not validated_point_items(
                [item], getattr(item, 'kr_currency_token', None)):
            raise RequestHumanTakeover('Unverified KR event-shop currency; no purchase input')
        self.event_shop_handle_obstruct()
        executed = False
        amount_handled = False
        timer = Timer(2, count=4).start()
        for _ in self.loop():
            if self.appear(AMOUNT_MAX, offset=(20, 20)):
                if not amount_handled:
                    self.device.click(AMOUNT_MAX)
                    if amount is not None:
                        self.ui_ensure_index(amount, letter=OCR_SHOP_AMOUNT, prev_button=AMOUNT_MINUS,
                                             next_button=AMOUNT_PLUS,
                                             skip_first_screenshot=False)
                    amount_handled = True
                    timer.reset()
                    continue
                else:
                    self.device.click(SHOP_BUY_CONFIRM_AMOUNT)
                    executed = True
                    timer.reset()
                    continue
            elif self.appear(SHOP_BUY_CONFIRM, offset=(20, 40)):
                self.device.click(SHOP_BUY_CONFIRM)
                executed = True
                timer.reset()
                continue
            #EN event shop uses different confirm compared to normal shop
            elif self.appear(SHOP_EVENT_BUY_CONFIRM, offset=(20, 40)):
                self.device.click(SHOP_EVENT_BUY_CONFIRM)
                executed = True
                timer.reset()
                continue
            elif self.handle_popup_confirm("meta_buy_confirm"):
                timer.reset()
                continue
            elif self.appear(BACK_ARROW_WHITE, offset=(20, 20)):
                if not executed:
                    if timer.reached():
                        self.device.click(item)
                        timer.reset()
                    continue
                elif timer.reached():
                    break
            elif timer.reached() and self.event_shop_handle_obstruct():
                timer.reset()
                continue

    def event_shop_handle_obstruct(self):
        if self.handle_info_bar():
            return True
        if self.handle_get_meowfficer():
            return True
        if self.appear(GET_SHIP, offset=(20, 20), interval=2):
            logger.info(f'Shop obstruct: {GET_SHIP} -> {SHOP_CLICK_SAFE_AREA}')
            self.device.click(SHOP_CLICK_SAFE_AREA)
            return True
        if self.appear(GET_ITEMS_1, offset=(20, 20), interval=2):
            logger.info(f'Shop obstruct: {GET_ITEMS_1} -> {SHOP_CLICK_SAFE_AREA}')
            self.device.click(SHOP_CLICK_SAFE_AREA)
            return True
        if self.appear(GET_ITEMS_3, offset=(20, 20), interval=2):
            logger.info(f'Shop obstruct: {GET_ITEMS_3} -> {SHOP_CLICK_SAFE_AREA}')
            self.device.click(SHOP_CLICK_SAFE_AREA)
            return True
        return False
