import importlib
import json
from pathlib import Path
import unittest


class Tempesta20261022Test(unittest.TestCase):
    def test_runtime_preserves_t_stage_names(self):
        from types import SimpleNamespace
        from module.campaign.run import CampaignRun
        runner = SimpleNamespace(config=SimpleNamespace(
            task=SimpleNamespace(command='Event'), STAGE_LOOP_ALIAS={}))
        folder = 'event_20261022_cn'
        for name in ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'SP'):
            with self.subTest(name=name):
                self.assertEqual(CampaignRun.handle_stage_name(runner, name, folder),
                                 (name.lower(), folder))

    def test_kr_schedule_does_not_change_other_regions(self):
        from module.config.config_updater import Event
        row = next(line for line in Path('campaign/Readme.md').read_text(encoding='utf-8').splitlines()
                   if 'event 20261022 cn' in line)
        event = Event(row)
        self.assertEqual(event.kr, '템페스타와 안개회랑')
        self.assertTrue(all(getattr(event, region) is None for region in ('cn', 'en', 'jp', 'tw')))

    def test_ghost_template_exists_and_decodes(self):
        from module.template import assets
        from PIL import Image
        self.assertIsNotNone(assets.TEMPLATE_SIREN_TempestaGhostBoss02)
        with Image.open('assets/cn/template/TEMPLATE_SIREN_TempestaGhostBoss02.gif') as im:
            for frame in range(im.n_frames):
                im.seek(frame)
                im.load()
            self.assertGreater(im.width, 0)

    def test_all_stage_modules_load(self):
        for stage in ('t1', 't2', 't3', 't4', 't5', 't6', 'sp'):
            with self.subTest(stage=stage):
                mod = importlib.import_module('campaign.event_20261022_cn.' + stage)
                self.assertEqual(mod.MAP.name, stage.upper())
                self.assertTrue(mod.Config.MAP_CHAPTER_SWITCH_20241219)
                self.assertEqual(sum(row.get('boss', 0) for row in mod.MAP.spawn_data), 1)

    def test_kr_event_selector_registered(self):
        data = json.loads(Path('module/config/argument/args.json').read_text(encoding='utf-8'))
        for task in ('Event', 'Event2', 'EventA', 'EventB', 'EventC', 'EventD', 'EventSp'):
            options = data[task]['Campaign']['Event']
            self.assertEqual(['event_20261022_cn'], options['option_kr'])
            self.assertIn('event_20261022_cn', options['option'])

    def test_kr_label_registered(self):
        data = json.loads(Path('module/config/i18n/ko-KR.json').read_text(encoding='utf-8'))
        self.assertIn('event_20261022_cn', data['Campaign']['Event'])
