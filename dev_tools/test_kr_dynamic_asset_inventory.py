"""Dynamically loaded Korean name templates are part of image coverage too."""
import unittest
from dev_tools import kr_asset_inventory


class DynamicAssetInventoryTest(unittest.TestCase):
    def test_item_and_season_name_assets_are_decodable_and_have_known_ids(self):
        rows = kr_asset_inventory.dynamic_name_inventory()
        self.assertGreaterEqual(len(rows), 80)
        self.assertTrue(any('island_item_name/2010_' in row['file'] for row in rows))
        self.assertTrue(any('island_task_name/' in row['file'] for row in rows))
        self.assertFalse([(row['file'], row['errors']) for row in rows if row['errors']])
        self.assertTrue(all(row['evidence'] == 'static-only' for row in rows))
