import re
from pathlib import Path

import cv2
import numpy as np

import module.config.server as server

from module.base.utils import color_similarity_2d, color_similar, rgb2luma, load_image
from module.logger import logger
from module.ocr.ocr import Ocr, Digit
from module.shop_event.selector import FILTER_REGEX
from module.statistics.item import Item, ItemGrid

ITEM_SHAPE = (63, 63)
GRID_SHAPE = (152, 206)
DELTA_PRICE_BACKGROUND = (14, 164)
DELTA_ITEM = (45, 44, 45 + ITEM_SHAPE[0], 33 + ITEM_SHAPE[1])
DELTA_AMOUNT = (13, 144, 136, 160)
DELTA_PRICE = (28, 164, 128, 193)
DELTA_TAG = (108, 30, 155, 52)
COUNTER_COLOR = (106, 120, 131)
COUNTER_THRESHOLD = 150
PRICE_THRESHOLD = 230
PRICE_BACKGROUND_COLOR = (61, 78, 91)
if server.server == 'kr':
    COUNTER_LEFT_STRIP = 52
elif server.server == 'jp':
    COUNTER_LEFT_STRIP = 54
elif server.server == 'en':
    COUNTER_LEFT_STRIP = 42
else:
    COUNTER_LEFT_STRIP = 70


class CounterOcr(Ocr):
    @staticmethod
    def parse_counter(value):
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]+/[0-9]+', value):
            logger.warning(f'Invalid counter format: {value}')
            return [0, 0]
        current, total = map(int, value.split('/'))
        if total <= 0 or current > total:
            logger.warning(f'Invalid counter range: {value}')
            return [0, 0]
        return [current, total]

    def __init__(self, buttons, lang='azur_lane', letter=(255, 255, 255), threshold=128,
                 alphabet='0123456789/IDSB', name=None):
        super().__init__(buttons, lang=lang, letter=letter, threshold=threshold, alphabet=alphabet, name=name)

    def pre_process(self, image):
        mask = color_similarity_2d(image, (255, 255, 255))
        brightness = np.min(mask, axis=0)
        match = np.where(brightness < COUNTER_THRESHOLD)[0]
        if len(match):
            left = match[0] + COUNTER_LEFT_STRIP
            total = mask.shape[1]
            if left < total:
                image = image[:, left:]
        image = super().pre_process(image)
        return image

    def after_process(self, result):
        result = super().after_process(result)
        result = result.replace('I', '1').replace('D', '0').replace('S', '5')
        result = result.replace('B', '8')
        # fixup result like "55" -> "5/5", "2530" -> "25/30"
        if result.isdigit():
            for total in [100, 50, 30, 40, 20, 10, 5, 4, 2, 1]:
                total_str = f'{total}'
                total_sep = f'/{total}'
                # Do not add a slash when the result is exactly the total,
                # e.g. "50" stays "50" instead of becoming "/50"
                if result.endswith(total_str) and result != total_str and not result.endswith(total_sep):
                    result = result[:-len(total_str)] + total_sep
        return result

    def ocr(self, image, direct_ocr=False):
        """
        Do OCR on a counter, such as `14/15`, and returns 14, 15

        Args:
            image:
            direct_ocr:

        Returns:
            list[list[int]: [[current, total]].
        """
        result_list = super().ocr(image, direct_ocr=direct_ocr)
        if isinstance(result_list, list):
            return [self.parse_counter(value) for value in result_list]
        return self.parse_counter(result_list)


class PriceOcr(Digit):
    def pre_process(self, image):
        mask = color_similarity_2d(image, PRICE_BACKGROUND_COLOR)
        brightness = np.min(mask, axis=0)
        match = np.where(brightness < PRICE_THRESHOLD)[0]
        if len(match):
            left = match[0] + 20
            total = mask.shape[1]
            if left < total:
                image = image[:, left:]
        image = super().pre_process(image)
        return image

PRICE_OCR = PriceOcr([], letter=(221, 221, 221), threshold=128, name='Price_ocr')


URPT_PRICE_IN_PT = 150  # 1 URpt costs 150 pt
COIN_PRICE_IN_URPT = 1  # 1 Coin costs 1 URpt
UR_SHIP_PRICES_IN_URPT = [200, 300]  # UR Ships cost 200 or 300 URpt


class EventShopItem(Item):
    IMAGE_SHAPE = ITEM_SHAPE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_ship = False
        self._scroll_pos = None
        self.total_count = -1
        self.count = 1

    def __str__(self):
        name = f'{self.name}_x{self.amount}_{self.count}/{self.total_count}_{self.cost}_x{self.price}'

        if self.tag is not None:
            name = f'{name}_{self.tag}'

        return name

    def predict_valid(self):
        luma = rgb2luma(self.image)
        return np.mean(luma > 127) >= 0.2

    @property
    def scroll_pos(self):
        return self._scroll_pos

    @scroll_pos.setter
    def scroll_pos(self, value):
        self._scroll_pos = value

    def __eq__(self, other):
        return id(self) == id(other)

    def correct_name_and_cost(self, save_unknown=True):
        if self.price in UR_SHIP_PRICES_IN_URPT and self.total_count == 1:
            self.name = 'ShipUR'
            self.cost = 'URpt'
            self.is_ship = True
        elif self.price == COIN_PRICE_IN_URPT and self.total_count == 350:
            # URpt to Coin
            self.name = 'Coin'
            self.cost = 'URpt'
        else:
            self.cost = 'pt'
            if self.price == 2000:
                if self.total_count == 10:
                    self.name = 'SkinBox'
                elif self.total_count == 4:
                    self.name = 'Meta'
                else:
                    self.name = 'EquipSSR'
            elif self.price == 8000:
                self.name = 'ShipSSR'
                self.is_ship = True
            elif self.price == 10000:
                self.name = 'EquipUR'
            elif self.price == URPT_PRICE_IN_PT and self.total_count == 500:
                self.name = 'URpt'
            elif self.name.isdigit() and save_unknown:
                logger.warning(f'Unrecognized item with price {self.price} and total count {self.total_count}, '
                               # f'defaulting to EquipSSR')
                               f'saving image for analysis.')
                import os
                from module.base.utils import save_image
                os.mkdir('assets/shop/event/new_templates/') if not os.path.exists('assets/shop/event/new_templates/') else None
                save_image(self.image, f'assets/shop/event/new_templates/{self.name}.png')
                # self.name = 'EquipSSR'

    def predict_genre(self):
        self.group, self.sub_genre, self.tier = None, None, None

        # Can use regular expression to quickly populate
        # the new attributes
        name = self.name.lower()
        result = re.search(FILTER_REGEX, name)
        if result:
            self.group, self.sub_genre, self.tier = \
            [group.lower()
             if group is not None else None
             for group in result.groups()]


class EventShopItemGrid(ItemGrid):
    item_class = EventShopItem

    def __init__(self,
                 grids,
                 templates,
                 template_area=(0, 0, ITEM_SHAPE[0], ITEM_SHAPE[1]),
                 amount_area=(31, 50, ITEM_SHAPE[0], ITEM_SHAPE[1]),
                 cost_area=(DELTA_PRICE[0] - DELTA_ITEM[0], DELTA_PRICE[1] - DELTA_ITEM[1],
                            DELTA_PRICE[2] - DELTA_ITEM[0], DELTA_PRICE[3] - DELTA_ITEM[1]),
                 price_area=(DELTA_PRICE[0] - DELTA_ITEM[0], DELTA_PRICE[1] - DELTA_ITEM[1],
                             DELTA_PRICE[2] - DELTA_ITEM[0], DELTA_PRICE[3] - DELTA_ITEM[1]),
                 tag_area=(DELTA_TAG[0] - DELTA_ITEM[0], DELTA_TAG[1] - DELTA_ITEM[1],
                           DELTA_TAG[2] - DELTA_ITEM[0], DELTA_TAG[3] - DELTA_ITEM[1]),
                 counter_area=(DELTA_AMOUNT[0] - DELTA_ITEM[0], DELTA_AMOUNT[1] - DELTA_ITEM[1],
                               DELTA_AMOUNT[2] - DELTA_ITEM[0], DELTA_AMOUNT[3] - DELTA_ITEM[1]),
                 ):
        super().__init__(grids, templates, template_area, amount_area, cost_area, price_area, tag_area)
        self.counter_ocr = CounterOcr([], letter=COUNTER_COLOR, name="CounterOcr")
        self.counter_area = counter_area
        self.price_ocr = PRICE_OCR
        self.kr_templates = {}
        if server.server == 'kr':
            for path in Path('./assets/shop/event_kr').glob('*.png'):
                # Omit the numeric amount and border; compare the actual icon.
                self.kr_templates[path.stem] = load_image(str(path))[:45, :63]

    def match_template(self, image, similarity=None):
        best_name, best_score = None, 0.97
        plate_matches = {}
        for name, template in self.kr_templates.items():
            score = cv2.minMaxLoc(cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED))[1]
            if name.startswith('Plate'):
                item_name = name.split('__', 1)[0]
                plate_matches[item_name] = max(score, plate_matches.get(item_name, 0))
            if score > best_score:
                best_name, best_score = name, score
        if best_name is not None:
            return best_name.split('__', 1)[0]
        # Fractional scroll rasterization can lower the correct plate match to
        # 0.967. Require both a high score and separation from other plates.
        plate_scores = sorted(((score, name) for name, score in plate_matches.items()), reverse=True)
        if len(plate_scores) >= 2 and plate_scores[0][0] >= 0.95 \
                and plate_scores[0][0] - plate_scores[1][0] >= 0.04:
            return plate_scores[0][1]
        return super().match_template(image, similarity=similarity)

    def predict_tag(self, image):
        color = cv2.mean(np.array(image))[:3]
        if color_similar(color1=color, color2=(255, 72, 72), threshold=50):
            return 'unobtained'
        return None

    def predict(self, image, name=True, amount=True, cost=False, price=True, tag=True, counter=True, scroll_pos=None,
                save_unknown=True):
        super().predict(image, name=name, amount=amount, cost=cost, price=price, tag=tag)
        if server.server == 'kr' and amount:
            for item in self.items:
                if item.name == 'SkinBox':
                    # This icon's white decoration resembles an extra 1.
                    # Keep the wide crop for four-digit oil/coin amounts.
                    item.amount = self.amount_ocr.ocr([item.crop((40, 50, 63, 63))], direct_ocr=True)[0]
        if counter and len(self.items):
            counter_list = [item.crop(self.counter_area) for item in self.items]
            counter_list = self.counter_ocr.ocr(counter_list, direct_ocr=True)
            for i, t in zip(self.items, counter_list):
                i.count, i.total_count = t

        if isinstance(scroll_pos, float) and len(self.items):
            for i in self.items:
                i.scroll_pos = scroll_pos

        for i in self.items:
            i.correct_name_and_cost(save_unknown=save_unknown)
            i.predict_genre()

        return self.items
