"""GUI-only event-shop inspection: navigation and OCR, never purchases."""
from module.exception import RequestHumanTakeover
from module.logger import logger
from module.shop_event.shop_event import EventShop


class EventShopScan(EventShop):
    scan_page = 0

    def schedule_next_run(self):
        logger.info('Inspection does not reschedule the regular EventShop task')

    def event_shop_get_items(self, scroll_pos=None):
        items = super().event_shop_get_items(scroll_pos=scroll_pos)
        self.scan_page += 1
        self.device.image_save('./log/kr_event_shop_scan_%02d.png' % self.scan_page)
        return items

    def _run(self):
        self.event_shop_load_ensure()
        self.get_current_pts()
        items = self.scan_all()
        logger.info('Read-only event shop scan complete: %s items; no purchases' % len(items))
        return True

    def event_shop_buy_item(self, *args, **kwargs):
        raise RequestHumanTakeover('Purchases are disabled in EventShopScan')

    def event_shop_buy_item_execute(self, *args, **kwargs):
        raise RequestHumanTakeover('Purchases are disabled in EventShopScan')
