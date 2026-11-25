"""New preparation text must not confuse old UI or the Handover tutorial."""
from unittest import TestCase
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
from module.map.kr_preparation import KR_MAP_PREPARATION
from module.base.button import Button
from module.base.base import ModuleBase
from module.base.utils import crop
from dev_tools.test_os_task_stop_boundaries import method


class PreparationTest(TestCase):
    def test_new_asset_matches_and_close_stays_in_observed_x(self):
        image = np.asarray(Image.open(KR_MAP_PREPARATION.file).convert('RGB'))
        self.assertTrue(KR_MAP_PREPARATION.match(image, offset=(80, 15), similarity=.9))
        self.assertEqual(KR_MAP_PREPARATION.move((45, -335)).button, (1060, 162, 1100, 192))

    def test_no_match_on_old_layout_or_tutorial_text(self):
        for name in ['assets/kr/map/MAP_PREPARATION.png',
                     'assets/kr/handler/KR_HANDOVER_TUTORIAL_3.png']:
            image = np.asarray(Image.open(name).convert('RGB'))
            self.assertFalse(KR_MAP_PREPARATION.match(image, offset=(80, 15), similarity=.9))

    def test_kr_clear_and_auto_switches_on_and_off(self):
        entries = json.loads(Path('dev_tools/kr_asset_overrides.json').read_text(encoding='utf-8'))['handler']
        symbols = {}
        image = np.zeros((720, 1280, 3), dtype=np.uint8)
        for name in ['AUTO_SEARCH_TITLE', 'AUTO_SEARCH_CHECK', 'CLEAR_MODE_TITLE', 'CLEAR_MODE_CHECK']:
            area = tuple(entries[name]['kr']['area'])
            file = 'assets/kr/handler/' + name + '.png'
            source = np.asarray(Image.open(file).convert('RGB'))
            image[area[1]:area[3], area[0]:area[2]] = crop(source, area)
            symbols[name] = Button(area=area, color=(0, 0, 0), button=area, file=file, name=name)
        symbols['AUTO_SEARCH_TITLE2'] = symbols['AUTO_SEARCH_TITLE']
        main = SimpleNamespace(appear=lambda b, offset: b.match(image, offset),
                               image_color_count=lambda area, **kw: ModuleBase.image_color_count(None, crop(image, area), **kw))
        auto = method('module/handler/fast_forward.py', 'SwitchAutoSearch', 'get', **symbols)
        clear = method('module/handler/fast_forward.py', 'SwitchClearMode', 'get', **symbols)
        self.assertEqual(auto(None, main), 'on')
        self.assertEqual(clear(None, main), 'on')
        image[589:605, 927:942] = 0
        image[586:606, 1044:1078] = 255
        self.assertEqual(auto(None, main), 'off')
        self.assertEqual(clear(None, main), 'off')
