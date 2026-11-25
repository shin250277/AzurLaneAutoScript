from dataclasses import replace
from datetime import datetime, timedelta

from module.base.button import Button, ButtonGrid
from module.base.decorator import cached_property, del_cached_property, has_cached_property
from module.base.timer import Timer
from module.base.template import Template
from module.base.utils import random_rectangle_vector_opted
from module.exception import RequestHumanTakeover
from module.island.assets import *
from module.island.data import DIC_ISLAND_PRODUCTION_PLACE, DIC_ISLAND_SLOT
from module.island_handler.dock import IslandDock
from module.island_handler.dock_scanner import CharacterScanner
from module.island_handler.recipe import IslandProductionRestart, IslandRecipe, KoreanRecipeNameUnknown
from module.base.utils import area_offset, area_pad, color_mask, random_rectangle_vector_opted
from module.exception import RequestHumanTakeover
from module.island.assets import *
from module.island.data import DIC_ISLAND_PRODUCTION_PLACE, DIC_ISLAND_SLOT
from module.island.utils import (
    get_configured_season, get_slot_ingredient_source_slots, item_name_with_id, production_place_name_with_id,
)
from module.island_handler.dock import IslandDock, dock_character_matches
from module.island_handler.exchange import FISH_MEAT_SOURCES
from module.island_handler.recipe import IslandProductionRestart, IslandRecipe
from module.island_handler.restaurant_config import (
    RESTAURANT_IDS,
    get_selected_named_waitresses,
    get_waitress_slots,
)
from module.logger import logger
from module.map_detection.utils import Points
from module.ui.page import page_island, page_island_manage


ANCHOR_AREA = (452, 7, 481, 36)
DETECT_AREA = (192, 69, 1221, 653)
NAME_AREA = (0, 0, 265, 39)
TAB_SIZE = (490, 159)
TAB_DELTA = (539, 183.5)
SLOT_ORIGIN = (62, 59)
SLOT_SIZE = (86, 86)
SLOT_DELTA = (95 - 1/3, 0)
TICK_AREA = (30, 35, 52, 51)
TICK_SEARCH_AREA = area_pad(TICK_AREA, pad=-2)
CHARACTER_SELECT_TITLE_AREA = (515, 144, 765, 202)
TEMPLATE_KR_PRODUCTION_CAFE_VARIANT = Template(file='./assets/kr/island/KR_PRODUCTION_CAFE_VARIANT.png')
KR_PRODUCTION_SELECT_CHARACTER = Button(
    area=(612, 328, 695, 351), color=(220, 220, 220),
    button=(620, 326, 690, 351),
    file='./assets/kr/island/KR_PRODUCTION_SELECT_CHARACTER.png', name='KR_PRODUCTION_SELECT_CHARACTER')

# Dedicated place skills, then shared skills. Names within each pool are unordered;
# the production dock sorts candidates by their current working efficiency.
# Unrestricted skills, such as Laffey's, use the general fallback.
PRODUCTION_WORKERS = {
    101: (('Saratoga', 'Chen_Hai'), ('Explorer', 'Hwah_Jah')),  # Farm
    102: (('Shimakaze', 'Nagato', 'Atago'), ()),  # Ranch
    201: (('Agir',), ()),  # Fishery
    401: (('Unicorn', 'Fei_Yuen'), ('Oceana',)),  # Mine
    402: (('New_Jersey', 'Mogador'), ('Oceana',)),  # Woods
    501: (('Taihou', 'Amagi_chan'), ('Explorer', 'Hwah_Jah')),  # Orchard
    502: (('Hood', 'Yat_Sen'), ('Explorer', 'Hwah_Jah')),  # Nursery
    601: (('Ying_Swei',), ('Chang_Feng',)),  # Golden Koi
    602: ((), ('Chang_Feng',)),  # Polar Bear
    603: ((), ('Chang_Feng',)),  # Manjuu Eatery
    604: ((), ('Chang_Feng',)),  # Grill
    703: (('Takao', 'Argus'), ()),  # Lumber
    704: (('William_D_Porter',), ()),  # Machinery
    706: (('Tashkent', 'Anchorage'), ()),  # Crafts
    901: (('Friedrich_der_Grosse', 'Belfast'), ('Chang_Feng',)),  # Cafe
}
# Natural Business A at level 50 without attribute training, excluding restaurant
# specialists covered by named waitress settings. Reserve these at stamina cap 150.
BUSINESS_WORKERS = {
    'Hood', 'Unicorn', 'Shimakaze', 'Javelin',
    'Yat_Sen', 'Fei_Yuen', 'Taihou', 'Argus',
}


def production_slot_name_with_id(slot_id):
    place_id = DIC_ISLAND_SLOT[slot_id]['place']
    return f'{production_place_name_with_id(place_id)} slot {slot_id}'


class IslandProduction(IslandRecipe, IslandDock):
    slot_finish_time = {}
    _first_run = True
    # Current place's roster in efficiency order; None until a complete scan.
    production_dock = None

    # main menu related methods
    def _get_tabs(self):
        area = (DETECT_AREA[0] + ANCHOR_AREA[0], DETECT_AREA[1] + ANCHOR_AREA[1], DETECT_AREA[2] - TAB_SIZE[0] + ANCHOR_AREA[2], DETECT_AREA[3] - TAB_SIZE[1] + ANCHOR_AREA[3])
        image = self.image_crop(area, copy=True)
        anchors = TEMPLATE_ISLAND_PRODUCTION_ANCHOR_ICON.match_multi(image, similarity=0.92, threshold=5)
        logger.attr('Production_tabs', len(anchors))
        rows = Points([(0., a.area[1]) for a in anchors]).group(threshold=5)
        return rows

    @cached_property
    def production_grid(self):
        for _ in self.loop(timeout=6):
            grid = self.get_production_grid()
            if len(grid.buttons) >= 4:
                return grid
        return grid

    def get_production_grid(self):
        rows = self._get_tabs()
        count = len(rows)
        if count < 2:
            logger.warning('Unable to find enough production tab anchors, assume tabs are at top')
            origin_y = 70
            delta_y = TAB_DELTA[1]
        elif count < 4:
            y_list = rows[:, 1]
            y1, y2 = y_list[0], y_list[-1]
            origin_y = min(y1, y2) + DETECT_AREA[1]
            delta_y = TAB_DELTA[1]
        else:
            logger.warning(f'Unexpected production tab anchor match result: {[a for a in rows]}')
            origin_y = 70
            delta_y = TAB_DELTA[1]

        production_grid = ButtonGrid(
            origin=(192, origin_y), delta=(TAB_DELTA[0], delta_y), button_shape=TAB_SIZE,
            grid_shape=(2, count), name='PRODUCTION_GRID'
        )
        return production_grid

    @cached_property
    def production_names(self):
        return self.get_production_codename()

    def get_production_codename(self):
        template_to_codename = {
            TEMPLATE_ISLAND_PRODUCTION_FIELD: 101,
            TEMPLATE_ISLAND_PRODUCTION_RANCH: 102,
            TEMPLATE_ISLAND_PRODUCTION_FISHERY: 201,
            TEMPLATE_ISLAND_PRODUCTION_MINE: 401,
            TEMPLATE_ISLAND_PRODUCTION_WOOD: 402,
            TEMPLATE_ISLAND_PRODUCTION_ORCHARD: 501,
            TEMPLATE_ISLAND_PRODUCTION_NURSERY: 502,
            TEMPLATE_ISLAND_PRODUCTION_KOI: 601,
            TEMPLATE_ISLAND_PRODUCTION_BEAR: 602,
            TEMPLATE_ISLAND_PRODUCTION_EATERY: 603,
            TEMPLATE_ISLAND_PRODUCTION_GRILL: 604,
            TEMPLATE_ISLAND_PRODUCTION_LUMBER: 703,
            TEMPLATE_ISLAND_PRODUCTION_MACHINERY: 704,
            TEMPLATE_ISLAND_PRODUCTION_ELECTRONIC: 705,
            TEMPLATE_ISLAND_PRODUCTION_CRAFTS: 706,
            TEMPLATE_ISLAND_PRODUCTION_CAFE: 901,
        }
        name_grid = self.production_grid.crop(NAME_AREA, name='PRODUCTION_NAME_GRID')
        if self.config.SERVER == 'kr':
            template_to_codename[TEMPLATE_KR_PRODUCTION_CAFE_VARIANT] = 901
        name_images = [self.image_crop(button.area, copy=True) for button in name_grid.buttons]
        codenames = []
        for image in name_images:
            for template, codename in template_to_codename.items():
                if template.match(image):
                    codenames.append(codename)
                    break
            else:
                logger.warning('Failed to recognize production name')
                codenames.append(None)
        places = [
            production_place_name_with_id(place_id)
            if place_id in DIC_ISLAND_PRODUCTION_PLACE else f'Unknown ({place_id})'
            for place_id in codenames
        ]
        logger.attr('Codenames', codenames)
        self._check_kr_production_names(codenames)
        logger.attr('Production_places', places)
        return codenames

    def _check_kr_production_names(self, codenames):
        if self.config.SERVER == 'kr' and (not codenames or None in codenames):
            self.device.image_save('./log/kr_island_production_unknown.png')
            raise RequestHumanTakeover('Korean production place name is not recognized; '
                                       'do not swipe repeatedly or guess a production slot.')

    @cached_property
    def slot_grids(self):
        return self.get_production_slot_grids()

    def get_production_slot_grids(self):
        slot_grids = {}
        names = self.production_names
        for codename, button in zip(names, self.production_grid.buttons):
            if codename not in DIC_ISLAND_PRODUCTION_PLACE:
                logger.warning(f'Codename {codename} not found in DIC_ISLAND_PRODUCTION_PLACE, skip slot grid creation')
                continue
            slot_length = len(DIC_ISLAND_PRODUCTION_PLACE[codename]['slot'])
            slot_grid = ButtonGrid(
                origin=(button.area[0] + SLOT_ORIGIN[0], button.area[1] + SLOT_ORIGIN[1]), delta=SLOT_DELTA, button_shape=SLOT_SIZE,
                grid_shape=(slot_length, 1), name=f'{codename}_SLOT_GRID'
            )
            slot_grids[codename] = slot_grid
        return slot_grids

    def is_slot_finished(self, slot_button: Button):
        if self.config.SERVER == 'kr':
            if self.config.SERVER == 'kr' and self.is_slot_empty(slot_button):
                return False
            tick_button = slot_button.crop(area=TICK_AREA, name=f'{slot_button.name}_TICK')
            return self.image_color_count(tick_button, (255, 255, 255), threshold=15, count=85)
        else:
            area = area_offset(TICK_SEARCH_AREA, slot_button.area[:2])
            image = self.image_crop(area, copy=False)
            white = color_mask(image, (255, 255, 255), threshold=15)
            return TEMPLATE_ISLAND_PRODUCTION_SLOT_TICK.match(white, similarity=0.70)

    def is_slot_empty(self, slot_button: Button):
        image = self.image_crop(slot_button.area, copy=True)
        return TEMPLATE_ISLAND_PRODUCTION_SLOT_EMPTY.match(image)

    def next_page(self):
        if 901 in self.production_names:
            logger.info('Already at last page, cannot swipe to next page')
            return False
        p1, p2 = random_rectangle_vector_opted((0, -450), box=(690, 70, 720, 650), padding=0)
        self.device.drag(p1, p2, hold_duration=0.1, name='PRODUCTION_NEXT_PAGE_SWIPE')
        del_cached_property(self, 'production_grid')
        del_cached_property(self, 'production_names')
        del_cached_property(self, 'slot_grids')
        for _ in self.loop(timeout=1):
            if self.handle_island_additional():
                break
        return True

    def prev_page(self):
        if 101 in self.production_names:
            logger.info('Already at first page, cannot swipe to previous page')
            return False
        p1, p2 = random_rectangle_vector_opted((0, 450), box=(690, 70, 720, 650), padding=0)
        self.device.drag(p1, p2, name='PRODUCTION_PREV_PAGE_SWIPE')
        del_cached_property(self, 'production_grid')
        del_cached_property(self, 'production_names')
        del_cached_property(self, 'slot_grids')
        for _ in self.loop(timeout=1):
            if self.handle_island_additional():
                break
        return True

    def ensure_top_page(self):
        for _ in self.loop():
            if 101 in self.production_names:
                break
            if not self.prev_page():
                break
        self.device.click_record_clear()

    def is_enter_window_shown(self):
        return self.image_color_count(CHARACTER_SELECT_TITLE_AREA, (62, 193, 255), threshold=30, count=6000)

    def claim_slot_reward(self, slot_button: Button):
        if not self.is_slot_finished(slot_button):
            logger.warning(f'Slot {slot_button} is not finished, cannot receive reward')
            return False
        for _ in self.loop(timeout=4):
            if self.handle_island_additional():
                continue
            if self.appear_then_click(ISLAND_PRODUCTION_RECEIVE, offset=(120, 20), interval=2):
                if self.config.SERVER == 'kr':
                    # Do not reopen the slot while its receive animation is
                    # still in flight. The following loop only closes popups.
                    break
                continue
            if self.ui_page_appear(page_island_manage, interval=2) and not self.is_enter_window_shown():
                self.device.click(slot_button)
                continue
            if self.is_enter_window_shown() and self.appear(ISLAND_PRODUCTION_SELECT_CHARACTER, offset=(60, 20)):
                break
        settled = Timer(2, count=3).start()
        for _ in self.loop(skip_first=False, timeout=15):
            if self.handle_island_additional():
                settled.reset()
                continue
            if self.is_enter_window_shown() or self.appear(ISLAND_PRODUCTION_RERUN, offset=(20, 20)):
                self.device.click(ISLAND_CLICK_SAFE_AREA)
                settled.reset()
                continue
            if self.match_template_color(page_island_manage.check_button) and not self.is_enter_window_shown() and not self.appear(ISLAND_PRODUCTION_SELECT_CHARACTER, offset=(60, 20)):
                if self.config.SERVER == 'kr' and not settled.reached():
                    continue
                if self.config.SERVER == 'kr' and self.is_slot_finished(slot_button):
                    self.device.image_save('./log/kr_island_production_unclaimed.png')
                    raise RequestHumanTakeover('Production reward remains unclaimed after closing the popup')
                return True
            settled.reset()
        self.device.image_save('./log/kr_island_production_close_timeout.png')
        raise RequestHumanTakeover('Production popup did not settle; do not swipe or dispatch')

    def confirm_korean_empty_slot(self, slot_button):
        # Read-only reconciliation for estimates left by an older process or
        # a manual claim. A busy/unknown slot must retain its pending estimate.
        for _ in range(3):
            self.device.screenshot()
            if (not self.ui_page_appear(page_island_manage)
                    or self.is_enter_window_shown()
                    or not self.is_slot_empty(slot_button)):
                return False
        return True

    def claim_reward_in_page(self, finished_slots=[]):
        for place_id, slot_grid in self.slot_grids.items():
            for slot_id, slot_button in zip(DIC_ISLAND_PRODUCTION_PLACE[place_id]['slot'], slot_grid.buttons):
                if self.is_slot_finished(slot_button) or self.slot_finish_time.get(slot_id, datetime.max) <= datetime.now():
                    if (self.config.SERVER == 'kr'
                            and self.slot_finish_time.get(slot_id, datetime.max) <= datetime.now()
                            and self.confirm_korean_empty_slot(slot_button)):
                        logger.info('Reconcile stale finish estimate for confirmed empty slot: %s' % slot_id)
                        del self.slot_finish_time[slot_id]
                        self.config.cross_set('IslandProduction.Storage.Storage.SlotFinishTime',
                                              {k: v.isoformat(sep=' ') for k, v in self.slot_finish_time.items()})
                        continue
                    if (self.config.SERVER == 'kr' and not self.is_slot_finished(slot_button)
                            and self.defer_korean_occupied_slot(slot_button)):
                        # A saved estimate can predate manual/new-season work.
                        # Keep it as evidence, but do not claim or replace this slot.
                        self.kr_deferred_slots = getattr(self, 'kr_deferred_slots', set()) | {slot_id}
                        logger.warning('Defer occupied KR slot with stale estimate, no input: %s' % slot_id)
                        continue
                    claimed = self.claim_slot_reward(slot_button)
                    if claimed is True:
                        self.claimed_slots.add(slot_id)
                    if self.config.SERVER == 'kr' and claimed is not True:
                        # A due estimate is not proof that the reward was received.
                        # Preserve the pending timestamp and do not dispatch over it.
                        raise RequestHumanTakeover('KR production reward was not confirmed; '
                                                   'retain pending finish time and stop')
                    if slot_id in self.slot_finish_time:
                        del self.slot_finish_time[slot_id]
                        if self.config.SERVER == 'kr':
                            # A later facility may fail before run() saves state.
                            # Persist only a confirmed claim, preserving other slots.
                            self.config.cross_set('IslandProduction.Storage.Storage.SlotFinishTime',
                                                  {k: v.isoformat(sep=' ') for k, v in self.slot_finish_time.items()})

                if place_id == 201 and self.is_slot_empty(slot_button):
                    self.has_empty_fishery_slot = True

    def defer_korean_occupied_slot(self, slot_button):
        for _ in range(3):
            self.device.screenshot()
            if (not self.ui_page_appear(page_island_manage) or self.is_enter_window_shown()
                    or self.is_slot_empty(slot_button) or self.is_slot_finished(slot_button)):
                return False
        return True

    def claim_all_rewards(self):
        logger.hr("Claim Production Rewards", level=2)
        self.claimed_slots = set()
        self.has_empty_fishery_slot = False
        self.ensure_top_page()
        while 1:
            self.claim_reward_in_page()
            if not self.next_page():
                break

    def select_production_character(self, place_id):
        pools = [pool for pool in PRODUCTION_WORKERS.get(place_id, ()) if pool]
        # Keep dedicated and shared workers within the places covered by their skills.
        blacklist = {
            name for groups in PRODUCTION_WORKERS.values() for pool in groups for name in pool
        }
        blacklist.difference_update(name for pool in pools for name in pool)
        for restaurant_id in RESTAURANT_IDS:
            slots = get_waitress_slots(self.config, restaurant_id)
            blacklist.update(get_selected_named_waitresses(slots))
        pools.append(None)  # General fallback accepts any eligible character.

        def available(character):
            if not dock_character_matches(
                    character, identity='any', emotion=(100, 150), emotion_limit=(100, 150),
                    blacklist=blacklist):
                return False
            return character.identity not in BUSINESS_WORKERS or character.emotion_limit < 150

        reverse = self.production_dock is None
        if reverse:
            dock = {}
            preferred = pools[0]

            def record_page(characters):
                for character in characters:
                    if character.identity in (None, '', 'unknown', 'Workerjuu'):
                        continue
                    # Preserve first-seen efficiency order, but never retain a button.
                    dock[character.identity] = replace(character, button=None)
                # The first eligible worker in the highest pool cannot be outranked later.
                for character in characters:
                    if (preferred is None or character.identity in preferred) and available(character):
                        return character
                return None

            logger.info(f'Scan production dock for {production_place_name_with_id(place_id)}')
            character, completed = self.island_dock_search(record_page, descending=True, disabled=('grade',))
            if character:
                logger.attr('Production worker', character.identity)
                # An early exit leaves the place roster incomplete; select this live button.
                return character if self.island_dock_select_one(character.button) else None
            if not completed:
                logger.warning('Production dock scan incomplete, discard roster')
                return None
            self.production_dock = dock
        else:
            dock = self.production_dock
            logger.info(f'Reuse production dock for {production_place_name_with_id(place_id)}')

        target = None
        for candidates in pools:
            target = next((character for character in dock.values()
                           if (candidates is None or character.identity in candidates) and available(character)), None)
            if target:
                break
        if target is None:
            if not reverse:
                # A new slot opens at the top; use the usual Workerjuu sort there.
                self.island_dock_sort_method_dsc_set(enable=False)
            return None
        logger.attr('Production worker', target.identity)

        def match_page(characters):
            for character in characters:
                if character.identity == target.identity:
                    return character if available(character) else False
            return None

        # The discovery pass ends at the bottom; later slots start at the top.
        character, _ = self.island_dock_search(
            match_page, descending=not reverse, reverse=reverse, disabled=('grade',))
        if character and self.island_dock_select_one(character.button):
            return character
        self.production_dock = None
        return None

    def handle_production_character_entry(self):
        if self.config.SERVER == 'kr':
            return (self.is_enter_window_shown() and self.appear_then_click(
                KR_PRODUCTION_SELECT_CHARACTER, offset=(20, 20), interval=1))
        return self.appear_then_click(ISLAND_PRODUCTION_SELECT_CHARACTER, offset=(60, 20), interval=1)

    def dispatch_slot(self, slot_id, slot_button, worker='manjuu', audit_only=False):
        if self.config.SERVER == 'kr' and not audit_only:
            if not getattr(self, 'kr_recipe_audit_complete', False):
                raise RequestHumanTakeover('KR production requires a completed current-run recipe audit')
            if slot_id not in getattr(self, 'kr_verified_recipe_slots', set()):
                raise RequestHumanTakeover('KR production requires a verified recipe group for this slot')
        if slot_id in DIC_ISLAND_PRODUCTION_PLACE[102]['slot']:
            del_cached_property(super(), 'recipe_id_sequence')
            del_cached_property(super(), 'all_recipe_stocks')
        for _ in self.loop(timeout=15 if self.config.SERVER == 'kr' else None):
            if self.is_in_island_dock():
                break
            if self.handle_production_character_entry():
                continue
            if self.match_template_color(page_island_manage.check_button, interval=1) and not self.is_enter_window_shown():
                self.device.click(slot_button)
                continue
        if self.config.SERVER == 'kr':
            if not self.is_in_island_dock():
                raise RequestHumanTakeover('Production character entry not confirmed; no repeated restart')
            if worker != 'manjuu':
                character = self.island_dock_find_character(worker)
                if not character or character.status != 'free':
                    logger.warning(f'Failed to select character {worker} for slot {slot_id}, try to select manjuu instead')
                    worker = 'manjuu'
                    self.ensure_dock_page_at_top()
                else:
                    self.island_dock_select_one(character.button)
            if worker == 'manjuu':
                self.island_dock_select_manjuu()
            self.island_dock_select_confirm(self.is_in_recipe_menu)
            if self.config.SERVER == 'kr':
                self.working_slot_id = slot_id
                del_cached_property(self, 'recipe_grid')
                del_cached_property(self, 'recipe_ids')
                stocks = self.scan_korean_dispatch_stocks(slot_id, audit_only)
                if stocks is None:
                    return False
                if audit_only:
                    self.ui_back(check_button=page_island_manage.check_button)
                    self.ensure_island_production_page()
                    for key in ('production_grid', 'production_names', 'slot_grids'):
                        del_cached_property(self, key)
                    return False  # No recipe start, ingredient purchase or exchange.
                if getattr(self, 'kr_potato_trial', False):
                    from module.island.potato_trial import run_trial
                    run_trial(self)
                if not getattr(self, 'kr_recipe_audit_complete', False):
                    raise RequestHumanTakeover('KR production requires a completed current-run recipe audit')
                # IslandRecipe.run retains final identity/stock protection guards.
                # Only the independently verified KR coin-material path may buy;
                # foreign-server purchasing/exchange branches remain unreachable.
            target_time = super().run(slot_id=slot_id)
        else:
            if self.config.IslandProduction_UseWorkerjuuByDefault:
                worker = self.island_dock_select_workerjuu()
            else:
                worker = self.select_production_character(DIC_ISLAND_SLOT[slot_id]['place'])
                if not worker:
                    logger.warning(
                        f'No available character for {production_slot_name_with_id(slot_id)}, '
                        'use Workerjuu for this slot'
                    )
                    worker = self.island_dock_select_workerjuu(descending=None)
            if not worker:
                logger.warning(f'Failed to select a worker for {production_slot_name_with_id(slot_id)}')
                self.island_dock_quit()
                return False
            emotion = float('inf') if worker.identity == 'Workerjuu' else worker.emotion
            logger.attr('Worker emotion', emotion)
            self.island_dock_select_confirm(self.is_in_recipe_menu)
            target_time = super().run(slot_id=slot_id, emotion=emotion)
        if target_time is not None:
            if self.config.SERVER != 'kr':
                dock = self.production_dock
                if dock and worker.identity in dock:
                    dock[worker.identity] = replace(dock[worker.identity], status='occupied')
            target_time = target_time.replace(microsecond=0)
            self.slot_finish_time[slot_id] = target_time
            if self.config.SERVER == 'kr':
                # A later facility can fail. Persist this confirmed start now,
                # without changing scheduler/protection settings or other slots.
                self.config.cross_set('IslandProduction.Storage.Storage.SlotFinishTime',
                                      {k: v.isoformat(sep=' ') for k, v in self.slot_finish_time.items()})
            for _ in self.loop(timeout=5):
                if self.handle_island_additional():
                    continue
                if self.match_template_color(page_island_manage.check_button, offset=(0, 20)):
                    if self.config.SERVER == 'kr':
                        self.settle_korean_dispatch_return()
                    return True
            self.ensure_island_production_page()
        else:
            logger.warning(f'Failed to start production for {production_slot_name_with_id(slot_id)}')
            if slot_id in [9031, 9032, 9033, 9034]:
                del_cached_property(super(), 'recipe_id_sequence')
                del_cached_property(super(), 'all_recipe_stocks')
            self.ui_back(check_button=page_island_manage.check_button)
            for _ in self.loop():
                if not self.is_enter_window_shown():
                    break
                self.device.click(ISLAND_CLICK_SAFE_AREA)
            self.ensure_island_production_page()
            return False

    def settle_korean_dispatch_return(self):
        """Do not classify other slots from the first returning animation frame."""
        settled = Timer(1, count=3).start()
        for _ in self.loop(timeout=6, skip_first=False):
            if self.handle_island_additional():
                settled.reset()
                continue
            if (self.match_template_color(page_island_manage.check_button, offset=(0, 20))
                    and not self.is_enter_window_shown()):
                if settled.reached():
                    for key in ('production_grid', 'production_names', 'slot_grids'):
                        del_cached_property(self, key)
                    return True
            else:
                settled.reset()
        raise RequestHumanTakeover('KR production return did not settle; preserve confirmed start')

    def scan_korean_dispatch_stocks(self, slot_id, audit_only):
        """Revoke only a failed identity group before any purchase/start."""
        try:
            stocks = self.scan_all_recipe_stocks()
            logger.attr('KR recipe probe', stocks)
            logger.attr('KR ingredient probe', self.probe_korean_recipe_counters(stocks))
            return stocks
        except KoreanRecipeNameUnknown:
            if audit_only or not self.is_in_recipe_menu():
                raise
            self.device.image_save('./log/kr_island_dispatch_name_{}.png'.format(slot_id))
            slot = DIC_ISLAND_SLOT[slot_id]
            siblings = {other for place in DIC_ISLAND_PRODUCTION_PLACE.values()
                        if slot_id in place['slot'] for other in place['slot']
                        if DIC_ISLAND_SLOT[other]['formula'] == slot['formula']
                        and DIC_ISLAND_SLOT[other]['activity_formula'] == slot['activity_formula']}
            self.kr_verified_recipe_slots.difference_update(siblings)
            logger.warning('Revoke KR recipe group after dispatch name failure: %s', sorted(siblings))
            self.ui_back(check_button=page_island_manage.check_button)
            self.ensure_island_production_page()
            for key in ('recipe_grid', 'recipe_ids'):
                del_cached_property(self, key)
            return None

    def probe_korean_recipe_counters(self, stocks):
        """Validate selection/counters without buying ingredients or starting work."""
        self.all_recipe_stocks = stocks
        results = {}
        for recipe_id in stocks:
            if not self.set_recipe(recipe_id):
                self.device.image_save('./log/kr_island_recipe_selection_unknown.png')
                raise RequestHumanTakeover('Korean recipe selection could not be verified')
            from module.island.kr_preflight import validate_recipe_counters
            from module.island_handler.recipe import ISLAND_RECIPE_AMOUNT_OCR
            from module.island.data import DIC_ISLAND_RECIPE
            from numbers import Integral
            amount = ISLAND_RECIPE_AMOUNT_OCR.ocr(self.device.image)
            active = self.get_active_recipe_id()
            if (DIC_ISLAND_RECIPE[recipe_id]['commission_cost'] == {} and active == recipe_id
                    and isinstance(amount, Integral) and not isinstance(amount, bool) and amount > 0):
                logger.info('KR recipe {}: no declared ingredients; selection-only audit, no start'.format(recipe_id))
                results[recipe_id] = None  # Not a verified ingredient counter or permission to start.
                continue
            counters = self.get_recipe_ingredient_counters()
            if active != recipe_id or not validate_recipe_counters(
                    DIC_ISLAND_RECIPE[recipe_id]['commission_cost'], amount, counters,
                    require_available=False,
                    components=getattr(self, 'recipe_ingredient_components', None)):
                self.device.image_save('./log/kr_island_ingredient_unknown.png')
                raise RequestHumanTakeover('Korean ingredient count/cost/balance could not be verified; no spending')
            if any(stock < required for stock, required, remaining in counters):
                logger.info('KR recipe {}: insufficient owned ingredients; audit only, no purchase'.format(recipe_id))
            results[recipe_id] = counters
        return results

    def dispatch_place(self, place_id, slots_to_check=None):
        if place_id not in self.slot_grids:
            place = (
                production_place_name_with_id(place_id)
                if place_id in DIC_ISLAND_PRODUCTION_PLACE else f'Unknown production place ({place_id})'
            )
            logger.error(f'{place} not found in current production page')
            return False
        place = production_place_name_with_id(place_id)
        if slots_to_check is not None and not slots_to_check.intersection(
                DIC_ISLAND_PRODUCTION_PLACE[place_id]['slot']):
            logger.info(f'Skip {place}: no new ingredients from completed production')
            return
        logger.info(f'Dispatch production place: {place}')
        self.production_dock = None
        slot_grid = self.slot_grids[place_id]
        is_first = True
        for index, (slot_id, slot_button) in enumerate(zip(
                DIC_ISLAND_PRODUCTION_PLACE[place_id]['slot'], slot_grid.buttons)):
            if slots_to_check is not None and slot_id not in slots_to_check:
                continue
            if self.config.SERVER == 'kr' and slot_id in getattr(self, 'kr_deferred_slots', set()):
                continue
            if (self.config.SERVER == 'kr'
                    and slot_id not in getattr(self, 'kr_verified_recipe_slots', set())):
                logger.warning('Skip unverified KR recipe group slot: %s' % slot_id)
                continue
            if not is_first and has_cached_property(super(), 'recipe_id_sequence') and not self.recipe_id_sequence:
                logger.info(f'No more recipe for place {place_id}, skip remaining slots')
                break
            if self.config.SERVER == 'kr':
                self.device.screenshot()
                for key in ('production_grid', 'production_names', 'slot_grids'):
                    del_cached_property(self, key)
                if place_id not in self.slot_grids:
                    return False  # Revisit when visible; do not mark it dispatched.
                slot_button = self.slot_grids[place_id].buttons[index]
            if self.is_slot_empty(slot_button):
                self.dispatch_slot(slot_id=slot_id, slot_button=slot_button)
            if is_first:
                is_first = False
        del_cached_property(super(), 'recipe_id_sequence')
        del_cached_property(super(), 'all_recipe_stocks')

    def audit_korean_recipes(self):
        """Inspect each distinct recipe group; never displace a working slot."""
        self.kr_verified_recipe_slots = set()
        self.kr_unresolved_recipe_groups = []
        inspected = set()
        unresolved = []
        for _ in range(40):
            self.ensure_top_page()
            probed = False
            for _ in range(20):
                grids = self.slot_grids
                if not grids:
                    raise RequestHumanTakeover('No verified KR facilities; audit incomplete')
                for place_id, grid in grids.items():
                    groups = {}
                    for slot_id, button in zip(DIC_ISLAND_PRODUCTION_PLACE[place_id]['slot'], grid.buttons):
                        slot = DIC_ISLAND_SLOT[slot_id]
                        key = (place_id, tuple(slot['formula']), tuple(slot['activity_formula']))
                        groups.setdefault(key, []).append((slot_id, button))
                    for key, slots in groups.items():
                        if key in inspected:
                            continue
                        inspected.add(key)
                        for slot_id, button in slots:
                            if slot_id in getattr(self, 'kr_deferred_slots', set()):
                                continue
                            if self.is_slot_empty(button):
                                try:
                                    self.dispatch_slot(slot_id, button, audit_only=True)
                                except KoreanRecipeNameUnknown:
                                    # Only a recognized recipe page may be left.
                                    # Keep gathering independent read-only evidence,
                                    # Unresolved groups never receive dispatch authority.
                                    if not self.is_in_recipe_menu():
                                        raise
                                    self.device.image_save('./log/kr_island_recipe_audit_{}_{}.png'.format(
                                        place_id, slot_id))
                                    self.ui_back(check_button=page_island_manage.check_button)
                                    self.ui_ensure(page_island_manage)
                                    del_cached_property(self, 'recipe_grid')
                                    del_cached_property(self, 'recipe_ids')
                                    unresolved.append((place_id, slot_id))
                                else:
                                    logger.attr('KR facility recipe audit complete', (place_id, slot_id))
                                    # Only sibling slots with exactly the same current
                                    # formula/activity group share this read-only audit.
                                    self.kr_verified_recipe_slots.update(s for s, _ in slots)
                                probed = True
                                break
                        if probed:
                            break
                        logger.attr('KR recipe group audit unavailable (no empty slot)', key)
                    if probed:
                        break  # Return changed the page; obtain fresh grids.
                if probed:
                    break
                if not self.next_page():
                    self.kr_unresolved_recipe_groups = unresolved
                    if unresolved:
                        logger.warning('Unresolved KR recipe groups remain blocked: %s' % unresolved)
                        if not self.kr_verified_recipe_slots:
                            raise RequestHumanTakeover('unresolved KR recipe groups {}; no production'.format(unresolved))
                    logger.info('KR facility recipe audit finished; no production started by audit')
                    return True
            if not probed:
                raise RequestHumanTakeover('KR facility audit page limit; no new production')
        raise RequestHumanTakeover('KR facility audit limit; no new production')

    def dispatch_all(self, check_all_empty_slots=False):
        if self.config.SERVER == 'kr':
            self.kr_recipe_audit_complete = False
            if not self.slot_grids:
                raise RequestHumanTakeover('No verified KR facilities; no production')
            if self.audit_korean_recipes() is not True:
                raise RequestHumanTakeover('KR recipe audit incomplete; no production')
            self.kr_recipe_audit_complete = True
        logger.hr("Dispatch Production", level=2)
        slots_to_check = None
        if not check_all_empty_slots:
            # Empty sources mean no upstream production to wait for.
            season = get_configured_season(self.config)
            slots_to_check = self.claimed_slots.copy()
            for slot_id in DIC_ISLAND_SLOT:
                sources = get_slot_ingredient_source_slots(slot_id, season)
                if not sources or self.claimed_slots.intersection(sources):
                    slots_to_check.add(slot_id)
            if not slots_to_check:
                logger.info('No completed production or external rewards to retry empty slots')
                return
        self.ensure_top_page()
        self.failed_buy_items = set()
        dispatched_places = set()
        while 1:
            try:
                for place_id in self.slot_grids.keys():
                    if place_id not in dispatched_places:
                        if self.dispatch_place(place_id, slots_to_check=slots_to_check) is not False:
                            dispatched_places.add(place_id)
                if not self.next_page():
                    break
            except IslandProductionRestart as e:
                if not e.success:
                    self.failed_buy_items.add(e.item_id)
                    logger.warning(
                        f'Failed to acquire ingredient {item_name_with_id(e.item_id)}; '
                        'restart production and skip further attempts for this item'
                    )
                else:
                    logger.info(
                        f'Acquired ingredient {item_name_with_id(e.item_id)}; '
                        'restart production from current page'
                    )
                del_cached_property(self, 'production_grid')
                del_cached_property(self, 'production_names')
                del_cached_property(self, 'slot_grids')
                continue

    def ensure_island_production_page(self):
        self.ui_ensure(page_island_manage)
        for _ in self.loop(timeout=10):
            if self.handle_island_additional():
                continue
            if self.ui_page_appear(page_island_manage, offset=(0, 20)):
                break
        self.island_manage_side_navbar_ensure(upper=1, skip_first_screenshot=False)
        for _ in self.loop():
            if self.config.SERVER == 'kr' and self.is_enter_window_shown():
                self.device.click(ISLAND_CLICK_SAFE_AREA)
                continue
            rows = self._get_tabs()
            count = len(rows)
            if count >= 2:
                break

    def exchange_surplus_fish(self):
        """
        Exchange fish above their hard floor, reserve and task target into fish meat,
        which holds more PT, and record the fish meat stock for fish production.
        """
        logger.hr("Exchange Surplus Fish", level=2)
        self.ui_goto_island_shop()
        keep = self.get_fish_keep_items()
        for meat_id in FISH_MEAT_SOURCES:
            result = self.island_exchange_fish_meat(meat_id, keep=keep)
            if result is not None:
                self.fish_meat_stock[meat_id] = result.after
        self.ui_back(check_button=page_island.check_button)
        self.ensure_island_production_page()

    def run(self):
        self.kr_deferred_slots = set()
        if self.config.SERVER == 'kr':
            from module.island_handler.kr_coin_material import recover_preview
            from module.ui.page import page_island_shop
            from module.ui_white.assets import BACK_ARROW_WHITE
            recover_preview(self)
            if self.ui_page_appear(page_island_shop):
                self.device.click(BACK_ARROW_WHITE)
                for _ in self.loop(timeout=10):
                    if (self.is_in_recipe_menu() or self.ui_page_appear(page_island_manage)
                            or self.ui_page_appear(page_island)):
                        break
                else:
                    raise RequestHumanTakeover('KR material shop return unrecognized; no guessed navigation')
        if self.config.SERVER == 'kr' and self.is_in_recipe_menu():
            self.ui_back(check_button=page_island_manage.check_button)
        self.ensure_island_production_page()
        slot_finish_time = self.config.cross_get("IslandProduction.Storage.Storage.SlotFinishTime", default={})
        self.slot_finish_time = {int(k): datetime.fromisoformat(v) for k, v in slot_finish_time.items()}
        self.fish_meat_stock = {}
        check_all_empty_slots = self.config.cross_get(
            "IslandProduction.Storage.Storage.CheckAllEmptySlots", default=False)
        # Keep a full check pending until this run's claims and dispatch finish.
        if not check_all_empty_slots:
            self.config.cross_set("IslandProduction.Storage.Storage.CheckAllEmptySlots", True)
        check_all_empty_slots = check_all_empty_slots or IslandProduction._first_run
        self.claim_all_rewards()
        yaml_text = self.config.cross_get("IslandProduction.IslandProduction.DailyBufferItems", "")
        if not yaml_text or yaml_text == "{}":
            logger.critical('No daily buffer items found in config, please run Island Production Planner first')
            raise RequestHumanTakeover('No daily buffer items found in config, please run Island Production Planner first')
        if (self.claimed_slots.intersection(DIC_ISLAND_PRODUCTION_PLACE[201]['slot'])
                or self.has_empty_fishery_slot):
            self.exchange_surplus_fish()
        self.dispatch_all(check_all_empty_slots=check_all_empty_slots)
        next_run_time = list(self.slot_finish_time.values())
        if self.config.SERVER == 'kr':
            # Retain historical estimates without scheduling an immediate loop.
            now = datetime.now()
            next_run_time = [stamp if stamp > now else now + timedelta(minutes=30)
                             for stamp in next_run_time]
        with self.config.multi_set():
            sorted_items = sorted(self.slot_finish_time.items(), key=lambda kv: (kv[1], kv[0]))
            slot_finish_time = {k: v.isoformat(sep=' ') for k, v in sorted_items}
            self.config.cross_set("IslandProduction.Storage.Storage.SlotFinishTime", slot_finish_time)
            self.config.cross_set("IslandProduction.Storage.Storage.CheckAllEmptySlots", False)
            if next_run_time:
                self.config.task_delay(target=next_run_time)
            else:
                self.config.task_delay(minute=30)
        IslandProduction._first_run = False
