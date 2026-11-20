import unittest
from dev_tools.kr_compatibility_audit import classify, assets, menu_coverage


class CompatibilityAuditTest(unittest.TestCase):
    def test_language_specific_fallback_is_not_shared(self):
        self.assertEqual(classify({'file': {'cn': 'cn/a', 'en': 'en/a',
                                          'jp': 'jp/a', 'tw': 'tw/a', 'kr': 'jp/a'}}),
                         'regional-fallback-review')

    def test_shared_file_with_different_crop_still_requires_review(self):
        self.assertEqual(classify({'file': dict.fromkeys(('cn', 'en', 'jp', 'tw', 'kr'), 'a'),
                                   'area': {'cn': (1,), 'en': (2,), 'jp': (1,),
                                            'tw': (1,), 'kr': (1,)}}),
                         'regional-fallback-review')

    def test_shared_and_localized_are_distinct(self):
        self.assertEqual(classify({'file': dict.fromkeys(('cn', 'en', 'jp', 'tw', 'kr'), 'a')}),
                         'upstream-shared')
        self.assertEqual(classify({'file': {'kr': './assets/kr/a.png'}}), 'kr-specific')
        self.assertEqual(classify({'file': {'jp': 'a'}}), 'missing-kr-mapping')

    def test_generated_assets_and_menu_are_accounted_for(self):
        rows = assets()
        self.assertGreater(len(rows), 1700)
        self.assertFalse([row for row in rows if row['classification'] == 'missing-kr-mapping'])
        self.assertFalse(menu_coverage()['not_documented'])


if __name__ == '__main__':
    unittest.main()
