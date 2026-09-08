"""Offline map/dependency checks; these do not certify KR live combat."""
import importlib
import json
from pathlib import Path
import unittest

from PIL import Image
from module.template import assets


ROOT = Path(__file__).resolve().parents[1]
EVENT = 'event_20260813_cn'
STAGES = [group + str(index) for group in 'abcd' for index in range(1, 4)] + ['sp']


class AstrariumMapsTest(unittest.TestCase):
    def test_maps_and_dependencies(self):
        for stage in STAGES:
            with self.subTest(stage=stage):
                module = importlib.import_module('campaign.' + EVENT + '.' + stage)
                width, height = module.MAP.shape
                rows = [row.split() for row in module.MAP.map_data.strip().splitlines()]
                self.assertEqual(len(rows), height + 1)
                self.assertTrue(all(len(row) == width + 1 for row in rows))
                self.assertTrue(any(row.get('boss') for row in module.MAP.spawn_data))
                for name in module.Config.MAP_SIREN_TEMPLATE:
                    self.assertIsNotNone(getattr(assets, 'TEMPLATE_SIREN_' + name, None))
                    with Image.open(ROOT / 'assets/cn/template' / ('TEMPLATE_SIREN_' + name + '.gif')) as image:
                        image.verify()

    def test_korean_event_option(self):
        args = json.loads((ROOT / 'module/config/argument/args.json').read_text(encoding='utf-8'))
        self.assertIn(EVENT, args['Event']['Campaign']['Event']['option_kr'])
        words = json.loads((ROOT / 'module/config/i18n/ko-KR.json').read_text(encoding='utf-8'))
        self.assertEqual(words['Campaign']['Event'][EVENT], '몽광의 아스트라리움')


if __name__ == '__main__':
    unittest.main()
