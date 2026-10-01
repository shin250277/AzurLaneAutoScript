"""Inspect Korean island pages without submitting orders or changing targets."""
from module.exception import RequestHumanTakeover
from module.logger import logger
from module.ui.page import page_island_order, page_island_season
from module.island.season_task import (IslandSeasonTask, ISLAND_SEASON_TASK_SCROLL,
                                      TEMPLATE_ISLAND_SEASON_TASK_OBTAINED)
from module.base.decorator import del_cached_property


class IslandInspect(IslandSeasonTask):
    def inspect_task_pages(self):
        """Bounded read-only scan; never return production targets to a caller."""
        ISLAND_SEASON_TASK_SCROLL.set_top(main=self, skip_first_screenshot=False)
        seen = set()
        for index in range(12):
            self.device.screenshot()
            self.device.image_save('./log/kr_island_inspect_tasks_%02d.png' % index)
            del_cached_property(self, 'season_task_grid')
            codes = self.get_task_codename()
            seen.update(code for code in codes if code is not None)
            logger.attr('Inspected season task codes', codes)
            logger.attr('Inspected completed task flags', [
                TEMPLATE_ISLAND_SEASON_TASK_OBTAINED.match(self.image_crop(button.area, copy=True))
                for button in self.season_task_grid.buttons])
            if ISLAND_SEASON_TASK_SCROLL.at_bottom(main=self):
                logger.attr('Unique inspected season tasks', len(seen))
                logger.info('Season task inspection reached bottom')
                return
            if index < 11:
                ISLAND_SEASON_TASK_SCROLL.next_page(main=self, page=0.5, skip_first_screenshot=False)
        logger.warning('Season inspection page limit reached; not a complete task scan')

    def run(self):
        if self.config.SERVER != 'kr':
            raise RequestHumanTakeover('This inspection tool is only for KR')
        self.device.image_save('./log/kr_island_inspect_initial.png')
        for page, name in [(page_island_order, 'order'), (page_island_season, 'season')]:
            self.ui_ensure(page)
            self.device.screenshot()
            self.device.image_save('./log/kr_island_inspect_%s.png' % name)
            logger.info(f'Island {name} page inspected; no submission or target changes')
        if not self.island_season_bottom_navbar_ensure(left=3):
            raise RequestHumanTakeover('Unable to inspect season task tab')
        self.device.screenshot()
        self.device.image_save('./log/kr_island_inspect_tasks.png')
        self.inspect_task_pages()
        logger.info('Island inspection complete; no task submission or target changes')
