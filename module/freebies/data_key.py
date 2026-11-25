from module.base.button import Button
from module.combat.assets import GET_ITEMS_1
from module.freebies.assets import *
from module.logger import logger
from module.ocr.ocr import DigitCounter
from module.ui.assets import CAMPAIGN_MENU_GOTO_WAR_ARCHIVES, WAR_ARCHIVES_CHECK
from module.ui.page import page_archives, page_campaign_menu
from module.ui.ui import UI


DATA_KEY = DigitCounter(OCR_DATA_KEY, letter=(255, 247, 247), threshold=64)

KR_DATA_KEY_COLLECT = Button(
    # KR keeps the button geometry but localizes its label, so the inherited
    # JP template cannot match. Use the stable brown button fill instead.
    area=(260, 40, 335, 71),
    color=(140, 108, 68),
    button=(251, 38, 339, 73),
    name='KR_DATA_KEY_COLLECT',
)

KR_DATA_KEY_COLLECTED = Button(
    area=(260, 40, 335, 71),
    color=(102, 103, 103),
    button=(251, 38, 339, 73),
    name='KR_DATA_KEY_COLLECTED',
)


class DataKey(UI):
    def _data_key_collect(self, skip_first_screenshot=True):
        """
        Pages:
            in: page_archives
            out: page_archives, DATA_KEY_COLLECTED
        """
        logger.hr('Data Key Collect')
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            collect = KR_DATA_KEY_COLLECT if self.config.SERVER == 'kr' else DATA_KEY_COLLECT
            collected = KR_DATA_KEY_COLLECTED if self.config.SERVER == 'kr' else DATA_KEY_COLLECTED

            if self.appear_then_click(
                    collect,
                    offset=0 if self.config.SERVER == 'kr' else (20, 20),
                    threshold=25,
                    interval=3):
                continue
            if self.appear(GET_ITEMS_1, offset=20, interval=3):
                self.device.click(collect)
                continue
            if self.handle_popup_confirm('DATA_KEY_LIMIT'):
                # If it's in 29/30 means user is not doing war achieves frequently,
                # no need to bother losing one key, just make it fulfilled.
                continue
            if self.appear_then_click(CAMPAIGN_MENU_GOTO_WAR_ARCHIVES, offset=(20, 20), interval=3):
                # Sometimes quit to page_campaign_menu accidentally.
                continue

            # End
            if self.appear(WAR_ARCHIVES_CHECK, offset=(20, 20)) and self.appear(
                    collected,
                    offset=0 if self.config.SERVER == 'kr' else (20, 20),
                    threshold=25):
                logger.info('Data key collect finished')
                break

    def data_key_collect(self):
        """
        Execute data key collection

        Returns:
            bool: If execute a collection.

        Pages:
            in: page_archives
        """
        collected = KR_DATA_KEY_COLLECTED if self.config.SERVER == 'kr' else DATA_KEY_COLLECTED
        if self.appear(
                collected,
                offset=0 if self.config.SERVER == 'kr' else (20, 20),
                threshold=25):
            logger.info('Data key has been collected')
            return False

        current, remain, total = DATA_KEY.ocr(self.device.image)
        logger.info(f'Inventory: {current} / {total}, Remain: {remain}')
        if not self.config.DataKey_ForceCollect and remain <= 0:
            logger.info('No more room for additional data key')
            return False

        self._data_key_collect()
        return True

    def run(self):
        """
        Handle data_key operations if configured to do so.

        Pages:
            in: page_any
            out: page_main
        """
        self.ui_ensure(page_archives)

        self.data_key_collect()

        # clear interval of pages, for faster switching on the next ui_goto()
        self.interval_clear([page_archives.check_button, page_campaign_menu.check_button])
