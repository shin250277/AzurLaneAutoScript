import unittest
from pathlib import Path


class FeatureInventoryTest(unittest.TestCase):
    def test_menu_and_task_source_have_identical_entries(self):
        from dev_tools.kr_feature_inventory import inventory
        rows = inventory()
        self.assertEqual(len(rows), len({r['task'] for r in rows}))
        self.assertTrue(all(r['in_menu'] and r['in_source'] for r in rows))

    def test_every_executable_task_has_a_handler(self):
        from dev_tools.kr_feature_inventory import inventory
        for row in inventory():
            if row['task'] not in ('Alas', 'General', 'EventGeneral', 'OpsiGeneral'):
                self.assertTrue(row['handler_exists'], row['task'])

    def test_review_document_has_every_task(self):
        from dev_tools.kr_feature_inventory import inventory
        text = Path('doc/KR_FEATURE_MATRIX.md').read_text(encoding='utf-8')
        for row in inventory():
            self.assertIn('| `' + row['task'] + '` |', text)


if __name__ == '__main__':
    unittest.main()
