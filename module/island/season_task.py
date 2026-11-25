from jellyfish import levenshtein_distance

from module.base.timer import Timer
from module.combat.assets import GET_ITEMS_1
import module.config.server as server
from module.base.button import ButtonGrid
from module.base.decorator import cached_property, del_cached_property
from module.island.assets import *
from module.island.data import DIC_ISLAND_TASK, DIC_ISLAND_ITEM
from module.island.kr_preflight import verified_season_targets
from module.island.ui import IslandUI
from module.island.utils import (
    get_configured_season, get_season_task_data,
    item_mapping_to_yaml, load_item_mapping, normalize_item_keys,
)
from module.logger import logger
from module.exception import RequestHumanTakeover
from module.map_detection.utils import Points
from module.ocr.ocr import Ocr
from module.ui.navbar import Navbar
from module.ui.page import page_island_season
from module.ui.scroll import Scroll


DETECT_AREA = (42, 171, 1206, 604)
ICON_AREA = (21, 133, 225, 195)
TAB_DELTA = (395, 230)
TAB_SIZE = (376, 211)
NAME_AREA = (29, 18, 270, 48)
ISLAND_SEASON_TASK_SCROLL = Scroll(
    ISLAND_SEASON_TASK_SCROLL_AREA.button,
    color=(128, 128, 128),
    name="ISLAND_SEASON_TASK_SCROLL"
)


def current_season_task_ids():
    from datetime import datetime, timezone
    from module.island.data import DIC_ISLAND_SEASON
    from module.config.utils import server_timezone, server_time_offset
    now = (datetime.now() - server_time_offset()).replace(tzinfo=timezone(server_timezone()))
    result = set()
    for season in DIC_ISLAND_SEASON.values():
        start = season.get('start_time', {}).get(server.server)
        end = season.get('end_time', {}).get(server.server)
        if not start or not end:
            continue
        start = datetime.fromisoformat(start).replace(tzinfo=timezone(server_timezone()))
        end = datetime.fromisoformat(end).replace(tzinfo=timezone(server_timezone()))
        if start <= now < end:
            result.update(season['task_list'])
    return result


class SeasonTaskNameOcr(Ocr):
    def after_process(self, result):
        result = super().after_process(result)
        if server.server != 'en' or not result:
            return result
        # Recover missing word spaces only when the existing task data gives
        # one exact match after removing whitespace. Other OCR text is retained.
        compact = ''.join(result.split())
        matches = {
            task['name']['en'] for task in DIC_ISLAND_TASK.values()
            if ''.join(task['name']['en'].split()) == compact
        }
        return next(iter(matches)) if len(matches) == 1 else result


class IslandSeasonTask(IslandUI):
    @cached_property
    def _island_season_bottom_navbar(self):
        """
        6 options:
            homepage,
            pt_reward,
            season_task,
            season_shop,
            season_rank,
            season_history
        """
        island_season_bottom_navbar = ButtonGrid(
            origin=(14, 677), delta=(213, 0),
            button_shape=(186, 33), grid_shape=(6, 1),
            name='ISLAND_SEASON_BOTTOM_NAVBAR'
        )
        return Navbar(grids=island_season_bottom_navbar,
                      active_color=(237, 237, 237),
                      inactive_color=(65, 78, 96),
                      active_count=500,
                      inactive_count=500)

    def island_season_bottom_navbar_ensure(self, left=None, right=None):
        """
        Args:
            left (int):
                1 for homepage,
                2 for pt_reward,
                3 for season_task,
                4 for season_shop,
                5 for season_rank,
                6 for season_history
            right (int):
                1 for season_history,
                2 for season_rank,
                3 for season_shop,
                4 for season_task,
                5 for pt_reward,
                6 for homepage

        """
        if self._island_season_bottom_navbar.set(self, left=left, right=right):
            return True
        return False

    def _get_icons(self):
        area = (DETECT_AREA[0] + ICON_AREA[0], DETECT_AREA[1] + ICON_AREA[1] - NAME_AREA[1], DETECT_AREA[2], DETECT_AREA[3])
        image = self.image_crop(area, copy=True)
        icons = TEMPLATE_ISLAND_SEASON_REWARD.match_multi(image, similarity=0.7, threshold=5)
        icons = Points([(0., icon.area[1]) for icon in icons]).group(threshold=5)
        logger.attr('icons_count', len(icons))
        return icons

    @cached_property
    def season_task_grid(self):
        for _ in self.loop(timeout=3):
            grid = self.get_season_task_grid()
            if len(grid.buttons) >= 3:
                return grid
        return grid

    def get_season_task_grid(self):
        rows = self._get_icons()
        count = len(rows)
        if count >= 2:
            y_list = rows[:, 1]
            y1, y2 = y_list[0], y_list[-1]
            origin_y = min(y1, y2) + DETECT_AREA[1] - NAME_AREA[1]
            delta_y = TAB_DELTA[1]
        elif count < 1:
            logger.warning('No icons detected, assume at top')
            origin_y = DETECT_AREA[1] - NAME_AREA[1]
            delta_y = TAB_DELTA[1]
        else:
            origin_y = rows[0][1] + DETECT_AREA[1] - NAME_AREA[1]
            delta_y = TAB_DELTA[1]

        season_task_grid = ButtonGrid(
            origin=(DETECT_AREA[0], origin_y),
            delta=(TAB_DELTA[0], delta_y),
            button_shape=TAB_SIZE,
            grid_shape=(3, count), name='SEASON_TASK_GRID'
        )
        return season_task_grid

    @cached_property
    def task_names(self):
        return self.get_task_codename()

    @property
    def task_name_ocr(self):
        if server.server == 'kr':
            from module.island.korean_season_ocr import KoreanSeasonTaskOcr
            return KoreanSeasonTaskOcr([], lang='ko', name='task_name_ocr_kr')
        if server.server == 'jp':
            lang = 'jp'
        elif server.server == 'tw':
            lang = 'tw'
        else:
            lang = 'cnocr'
        ocr = SeasonTaskNameOcr([], lang=lang, letter=(57, 58, 60), name='task_name_ocr')
        return ocr

    def get_task_codename(self):
        name_grid = self.season_task_grid.crop(NAME_AREA, name='TASK_NAME_GRID')
        name_images = [self.image_crop(button.area, copy=True) for button in name_grid.buttons]
        names = self.task_name_ocr.ocr(name_images, direct_ocr=True)
        codenames = [self.task_name_to_codename(name) for name in names]
        logger.attr('Codenames', codenames)
        return codenames

    def task_name_to_codename(self, name):
        if not isinstance(name, str):
            return None

        if server.server == 'kr':
            from module.island.data import DIC_ISLAND_SEASON
            from module.config.utils import server_timezone, server_time_offset
            from datetime import datetime, timezone

            server_now = (datetime.now()-server_time_offset()).replace(tzinfo=timezone(server_timezone()))
            current_season_task_ids= set()
            for season_data in DIC_ISLAND_SEASON.values():
                if not season_data['start_time'] or not season_data['end_time']:
                    continue
                season_start_string = season_data['start_time'].get(server.server)
                season_end_string = season_data['end_time'].get(server.server)
                if not season_start_string or not season_end_string:
                    continue
                season_start= datetime.fromisoformat(season_start_string).replace(tzinfo=timezone(server_timezone()))
                season_end= datetime.fromisoformat(season_end_string).replace(tzinfo=timezone(server_timezone()))
                if season_start <= server_now < season_end:
                    current_season_task_ids.update(season_data['task_list'])
        else:
            current_season_task_ids = get_configured_season(self.config)['task_list']
        if not current_season_task_ids:
            logger.warning(f'No tasks found for the configured season on {server.server} server.')
            return None

        if server.server == 'kr':
            # Never turn empty/unknown Hangul into a production target by
            # selecting the least-bad fuzzy match. Ambiguous names fail closed.
            normalized = ''.join(name.split())
            matches = [key for key in current_season_task_ids
                       if normalized and normalized == ''.join(
                           DIC_ISLAND_TASK.get(key, {}).get('name', {}).get('kr', '').split())]
            if len(matches) == 1:
                return matches[0]
            logger.warning(f'Unknown or ambiguous KR season task: {name!r}')
            return None
        
        min_distance = float('inf')
        code = None
        corrected_name = None

        for key in current_season_task_ids:
            if key not in DIC_ISLAND_TASK:
                continue
            item = get_season_task_data(key)
            distance = levenshtein_distance(name, item['name'][server.server])
            if distance <= min_distance:
                # allow for multiple matches, but only keep the closest one
                min_distance = distance
                code = key
                corrected_name = item['name'][server.server]
        if name != corrected_name:
            logger.warning(f'Task name corrected: {name} -> {corrected_name}')
        return code

    def handle_island_get_items(self):
        if self.appear(GET_ITEMS_1, offset=(20, 100), interval=3):
            self.device.click(ISLAND_SEASON_TASK_RECEIVE_ALL)
            return True
        if self.has_white_band():
            if self.appear(page_island_season.check_button):
                return False
            self.device.click(ISLAND_SEASON_TASK_RECEIVE_ALL)
            return True
        return False

    def receive_all_reward(self):
        clicked = False
        confirm_timer = Timer(3, count=6)
        for _ in self.loop(skip_first=False):
            if self.appear_then_click(ISLAND_SEASON_TASK_RECEIVE_ALL, interval=2, offset=(20, 20)):
                clicked = True
                confirm_timer.reset()
                continue
            if self.handle_island_additional():
                confirm_timer.reset()
                continue
            if confirm_timer.reached():
                if clicked:
                    logger.info('Receive all rewards confirmed')
                else:
                    logger.info('No rewards to receive')
                break

    def scan_all(self, capture_progress=False):
        if capture_progress:
            self._kr_task_progress = {}
        ISLAND_SEASON_TASK_SCROLL.set_top(main=self, skip_first_screenshot=False)
        logger.hr('scanning season tasks')
        unfinished_tasks = []
        early_stop = False
        page_count = 0
        verified_pages = set()
        while 1:
            page_count += 1
            if self.config.SERVER == 'kr' and (
                    page_count > 20 or not self.task_names
                    or len(self.task_names) != len(self.season_task_grid.buttons)):
                self.device.image_save('./log/kr_island_season_scan_invalid.png')
                raise RequestHumanTakeover('Incomplete KR season scan; preserve production targets')
            counters = None
            if capture_progress:
                counter_grid = self.season_task_grid.crop((285, 18, 365, 48))
                counters = Ocr(counter_grid.buttons, lang='cnocr', letter=(102, 108, 112),
                               threshold=128, alphabet='0123456789/').ocr(self.device.image)
                if not isinstance(counters, list) or len(counters) != len(self.task_names):
                    raise RequestHumanTakeover('Incomplete KR season counters; no submission')
            for index, (task_id, button) in enumerate(zip(self.task_names, self.season_task_grid.buttons)):
                image = self.image_crop(button.area, copy=True)
                obtained = bool(TEMPLATE_ISLAND_SEASON_TASK_OBTAINED.match(image))
                if capture_progress:
                    if task_id is None:
                        raise RequestHumanTakeover('Unknown KR task in claim audit; no submission')
                    evidence = (counters[index], obtained)
                    old = self._kr_task_progress.get(task_id)
                    if old is not None and old != evidence:
                        raise RequestHumanTakeover('KR task changed while scanning; no submission')
                    self._kr_task_progress[task_id] = evidence
                if obtained:
                    if self.config.SERVER == 'kr':
                        # Do not assume every later card is also obtained.
                        # Goal updates require reaching the actual list end.
                        continue
                    early_stop = True
                    break
                if task_id is None:
                    if self.config.SERVER == 'kr':
                        self.device.image_save('./log/kr_island_season_unknown.png')
                        raise RequestHumanTakeover('Unknown KR season task; preserve production targets')
                    logger.warning('Unable to identify season task, skip it')
                    continue
                else:
                    if task_id not in unfinished_tasks:
                        unfinished_tasks.append(task_id)
            if self.config.SERVER == 'kr' and all(task is not None for task in self.task_names):
                # A newly identified page proves progress, unlike repeating
                # the same swipe. Remove only this scroll's history, leaving
                # unrelated input guards and the 20-page scan bound intact.
                new_tasks = set(self.task_names) - verified_pages
                if new_tasks:
                    self.device.click_record_remove(ISLAND_SEASON_TASK_SCROLL.name)
                    verified_pages.update(self.task_names)
            if early_stop:
                logger.info(f'Detect obtained task, early stop scanning')
                break
            if ISLAND_SEASON_TASK_SCROLL.at_bottom(main=self):
                break
            else:
                # KR reward anchors expose only fully visible rows. The
                # default 0.8-page jump can skip a row between observations.
                ISLAND_SEASON_TASK_SCROLL.next_page(
                    main=self, page=0.4 if self.config.SERVER == 'kr' else 0.8,
                    skip_first_screenshot=False)
                del_cached_property(self, 'season_task_grid')
                del_cached_property(self, 'task_names')
                continue
        logger.info(f'Unfinished tasks: {unfinished_tasks}')
        return unfinished_tasks

    def audit_korean_season(self, return_verified=False, capture_progress=False):
        """Exercise navigation/OCR without claiming or changing the production plan."""
        active = current_season_task_ids() if return_verified else None
        if return_verified and not active:
            raise RequestHumanTakeover('No verified active KR season; preserve production targets')
        self.ui_ensure(page_island_season)
        self.island_season_bottom_navbar_ensure(left=3)
        del_cached_property(self, 'season_task_grid')
        del_cached_property(self, 'task_names')
        unfinished = self.scan_all(capture_progress=True) if capture_progress else self.scan_all()
        if capture_progress and set(self._kr_task_progress) != active:
            raise RequestHumanTakeover('Incomplete KR claim task coverage; no submission')
        verified = None
        if return_verified:
            verified = verified_season_targets(unfinished, active, DIC_ISLAND_TASK, DIC_ISLAND_ITEM)
            if active != current_season_task_ids() or verified is None:
                raise RequestHumanTakeover('KR season evidence changed or invalid; preserve production targets')
        proposed = {}
        for task_id in unfinished:
            for item_id, amount in DIC_ISLAND_TASK[task_id]['target'].items():
                proposed[item_id] = proposed.get(item_id, 0) + amount
        logger.attr('KR season audit tasks', unfinished)
        logger.attr('KR season audit candidate (not applied)', proposed)
        self.device.image_save('./log/kr_island_season_audit.png')
        if return_verified:
            if verified != proposed:
                raise RequestHumanTakeover('KR season evidence changed or invalid; preserve production targets')
            return verified
        raise RequestHumanTakeover('KR season scan complete; production target update remains blocked pending validation')

    def sync_korean_season(self, claim=False):
        """Update only verified goals, never export planner settings or buy items."""
        active = current_season_task_ids()
        if claim:
            from module.island.kr_season_claim import PENDING_KEY
            if self.config.cross_get(PENDING_KEY, None):
                raise RequestHumanTakeover('Unresolved KR season claim; do not automatically retry')
            first = self.audit_korean_season(return_verified=True, capture_progress=True)
            first_progress = dict(self._kr_task_progress)
            second = self.audit_korean_season(return_verified=True, capture_progress=True)
            if first_progress != self._kr_task_progress:
                raise RequestHumanTakeover('KR claim counters disagree; no submission')
        else:
            first = self.audit_korean_season(return_verified=True)
            second = self.audit_korean_season(return_verified=True)
        if not active or active != current_season_task_ids() or first != second:
            raise RequestHumanTakeover('KR season scans disagree; preserve production targets')
        if claim and self.claim_korean_season_rewards():
            return self.sync_korean_season(claim=False)
        yaml_text = self.config.cross_get('IslandSeasonTask.IslandSeasonTask.TaskTarget', '{}')
        old = normalize_item_keys(load_item_mapping(yaml_text, config_name='TaskTarget'))
        if second != old:
            self.config.cross_set('IslandSeasonTask.IslandSeasonTask.TaskTarget',
                                  item_mapping_to_yaml(second, use_item_name=True))
        self.config.task_delay(server_update=True)

    def claim_korean_season_rewards(self):
        from datetime import datetime
        from module.island.kr_season_claim import claimable_tasks, PENDING_KEY
        from module.island.utils import load_hard_floor_items
        from module.island_handler.restaurant_config import get_menu_reserve_items
        protected = normalize_item_keys(load_hard_floor_items(
            self.config.cross_get('IslandProduction.IslandProduction.HardFloorItems', '{}')))
        for item, amount in get_menu_reserve_items(self.config).items():
            protected[item] = protected.get(item, 0) + amount
        ready = claimable_tasks(self._kr_task_progress, DIC_ISLAND_TASK, protected)
        if ready is None:
            raise RequestHumanTakeover('Invalid KR claim quantities; no submission')
        if not ready:
            logger.info('KR season: no claim permitted by completion/stock protections')
            return False
        self.device.screenshot()
        if not self.match_template_color(ISLAND_SEASON_TASK_RECEIVE_ALL, offset=(0, 0)):
            raise RequestHumanTakeover('KR season claim control not verified; no submission')
        self.config.cross_set(PENDING_KEY, {'tasks': ready, 'at': datetime.now().isoformat()})
        self.config.update()
        self.device.image_save('./log/kr_season_claim_before.png')
        self.device.click(ISLAND_SEASON_TASK_RECEIVE_ALL)
        # Exactly one submission. No click retry when acknowledgement is unclear.
        for _ in self.loop(timeout=8, skip_first=False):
            self.handle_island_additional()
        self.audit_korean_season(return_verified=True, capture_progress=True)
        after = dict(self._kr_task_progress)
        self.audit_korean_season(return_verified=True, capture_progress=True)
        if (after != self._kr_task_progress
                or any(not after.get(task, (None, False))[1] for task in ready)):
            raise RequestHumanTakeover('KR claim acknowledgement uncertain; automatic retry blocked')
        self.config.cross_set(PENDING_KEY, None)
        logger.info('KR season claims confirmed: %s' % ready)
        return True

    def run(self):
        if self.config.SERVER == 'kr':
            return self.sync_korean_season(claim=True)
        self.ui_ensure(page_island_season)
        self.island_season_bottom_navbar_ensure(left=3)
        self.receive_all_reward()
        yaml_text = self.config.cross_get("IslandSeasonTask.IslandSeasonTask.TaskTarget", "{}")
        old_target = normalize_item_keys(load_item_mapping(yaml_text, config_name='TaskTarget'))
        new_target = {}
        unfinished_tasks = self.scan_all()
        for task_id in unfinished_tasks:
            target = get_season_task_data(task_id)['target']
            if target:
                item_id = list(target.keys())[0]
                new_target[item_id] = new_target.get(item_id, 0) + target[item_id]
        new_target = normalize_item_keys(new_target)
        target_changed = new_target != old_target
        if target_changed:
            yaml_text = item_mapping_to_yaml(new_target, use_item_name=True)
            self.config.cross_set("IslandSeasonTask.IslandSeasonTask.TaskTarget", yaml_text)
            logger.info('Re-running production planner because season-task targets changed')
            from module.island_handler.production_planner import IslandProductionPlanner
            IslandProductionPlanner(self.config, self.device).run()
        self.config.task_delay(server_update=True)
