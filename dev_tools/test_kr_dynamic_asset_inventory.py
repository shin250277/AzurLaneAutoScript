"""Dynamically loaded Korean name templates are part of image coverage too."""
import unittest
from pathlib import Path
from PIL import Image
from dev_tools import kr_asset_inventory


class DynamicAssetInventoryTest(unittest.TestCase):
    def test_kr_recipe_icon_cores_have_known_ids_and_fit_observed_cards(self):
        from module.island.data import DIC_ISLAND_ITEM
        paths = list(Path('assets/kr/island_recipe_icon').glob('*.png'))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIn(int(path.stem), DIC_ISLAND_ITEM)
                with Image.open(str(path)) as im:
                    self.assertEqual(im.mode, 'RGB')
                    self.assertTrue(32 <= im.width <= 95 and 32 <= im.height <= 95)
                    im.load()

    def test_item_and_season_name_assets_are_decodable_and_have_known_ids(self):
        rows = kr_asset_inventory.dynamic_name_inventory()
        self.assertGreaterEqual(len(rows), 80)
        self.assertTrue(any('island_item_name/2010_' in row['file'] for row in rows))
        self.assertTrue(any('island_task_name/' in row['file'] for row in rows))
        self.assertFalse([(row['file'], row['errors']) for row in rows if row['errors']])
        self.assertTrue(all(row['evidence'] == 'static-only' for row in rows))
