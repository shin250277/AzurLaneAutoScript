"""Configuration labels can fall back; unknown Korean OCR must not be guessed."""
import unittest
from unittest.mock import patch

import module.config.server as server
from module.island.data import DIC_ISLAND_ITEM
from module.island.utils import item_name, item_export_key, normalize_item_id


class KoreanIslandItemNameTest(unittest.TestCase):
    def test_missing_korean_labels_export_stable_id(self):
        with patch.object(server, 'server', 'kr'):
            for item_id, item in DIC_ISLAND_ITEM.items():
                with self.subTest(item=item_id):
                    label = item_name(item_id)
                    self.assertEqual(label, item['name'].get('kr') or item['name'].get('en') or str(item_id))
                    self.assertEqual(normalize_item_id(item_export_key(item_id, True)), item_id)

    def test_unknown_korean_name_is_rejected_not_matched_to_foreign_name(self):
        with patch.object(server, 'server', 'kr'):
            with self.assertRaises(ValueError):
                normalize_item_id('확인되지 않은 한국어 품목')

    def test_verified_korean_name_wins_and_other_servers_are_unchanged(self):
        names = DIC_ISLAND_ITEM[1000]['name']
        with patch.dict(names, {'kr': '검증용 품목'}), patch.object(server, 'server', 'kr'):
            self.assertEqual(item_name(1000), '검증용 품목')
            self.assertEqual(normalize_item_id('검증용 품목'), 1000)
        with patch.object(server, 'server', 'jp'):
            self.assertEqual(item_name(1000), names['jp'])


if __name__ == '__main__':
    unittest.main()
