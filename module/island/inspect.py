"""Inspect Korean island pages without submitting orders or changing targets."""
from module.exception import RequestHumanTakeover
from module.logger import logger
from module.ui.page import page_island_order, page_island_season
from module.ui.ui import UI


class IslandInspect(UI):
    def run(self):
        if self.config.SERVER != 'kr':
            raise RequestHumanTakeover('This inspection tool is only for KR')
        self.device.image_save('./log/kr_island_inspect_initial.png')
        for page, name in [(page_island_order, 'order'), (page_island_season, 'season')]:
            self.ui_ensure(page)
            self.device.screenshot()
            self.device.image_save('./log/kr_island_inspect_%s.png' % name)
            logger.info(f'Island {name} page inspected; no submission or target changes')
        logger.info('Island inspection complete; task OCR is not yet validated')
