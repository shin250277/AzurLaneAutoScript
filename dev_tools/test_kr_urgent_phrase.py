from unittest import TestCase
from unittest.mock import Mock
from types import SimpleNamespace
from PIL import Image
import numpy as np
from module.handler.info_handler import KR_GET_MISSION_TEXT, KR_GET_MISSION
from dev_tools.test_os_task_stop_boundaries import method


class UrgentPhraseTest(TestCase):
    def handle(self, image, button=True):
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui._hot_fix_check_wait.reached.return_value = False
        ui._hot_fix_check_wait.started.return_value = False
        def appear(b, **kw):
            if b is KR_GET_MISSION:
                return button
            if b is KR_GET_MISSION_TEXT:
                if 'offset' in kw:
                    return b.match(image, offset=kw['offset'], similarity=kw['similarity'])
                return b.appear_on(image, threshold=kw['threshold'])
            return False
        ui.appear.side_effect = appear
        fn = method('module/handler/info_handler.py', 'InfoHandler', 'handle_urgent_commission',
                    KR_GET_MISSION_TEXT=KR_GET_MISSION_TEXT, KR_GET_MISSION=KR_GET_MISSION)
        fn(ui)
        return ui.device.click.call_count

    def test_phrase_matches_variable_commission_name_lengths(self):
        source = np.asarray(Image.open('assets/kr/handler/KR_URGENT_PHRASE.png').convert('RGB'))
        for dx in (-80, 0, 80):
            with self.subTest(dx=dx):
                self.assertEqual(self.handle(np.roll(source, dx, axis=1)), 1)

    def test_confirm_button_alone_never_accepted(self):
        self.assertEqual(self.handle(np.zeros((720, 1280, 3), dtype=np.uint8)), 0)

    def test_phrase_without_confirm_never_clicked(self):
        source = np.asarray(Image.open('assets/kr/handler/KR_URGENT_PHRASE.png').convert('RGB'))
        self.assertEqual(self.handle(source, button=False), 0)
