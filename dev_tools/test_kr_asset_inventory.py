"""Static image integrity is not evidence of matching a live KR screen."""
import unittest

from dev_tools.kr_asset_inventory import inspect_asset, inventory


class AssetInventoryTest(unittest.TestCase):
    def test_missing_file_is_not_compatible(self):
        row = inspect_asset('missing', 'Button', {'file': './assets/missing.png',
                                                'area': (0, 0, 10, 10)})
        self.assertTrue(row['errors'])

    def test_invalid_coordinates_are_rejected(self):
        row = inspect_asset('bad', 'Button', {
            'file': './assets/kr/os/FLEET_1.png', 'area': (50, 20, 10, 30)})
        self.assertIn('invalid area', row['errors'])

    def test_foreign_asset_is_not_promoted_to_observed_kr(self):
        row = inspect_asset('shared', 'Template', {'file': './assets/jp/os/FLEET_1.png'})
        self.assertEqual(row['evidence'], 'static-only')
        self.assertEqual(row['source'], 'foreign-or-shared')

    def test_inventory_is_complete_and_decodable(self):
        rows = inventory()
        self.assertGreater(len(rows), 1700)
        self.assertFalse([(r['id'], r['errors']) for r in rows if r['errors']])
