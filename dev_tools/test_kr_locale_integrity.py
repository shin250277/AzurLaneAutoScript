"""Structural locale checks; passing does not prove translation quality."""
import json
from pathlib import Path
import re
import unittest


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate locale key: ' + key)
        result[key] = value
    return result


def flatten(node, prefix=()):
    result = {}
    for key, value in node.items():
        path = prefix + (key,)
        if isinstance(value, dict):
            result.update(flatten(value, path))
        else:
            result[path] = value
    return result


class KoreanLocaleIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / 'module/config/i18n'
        cls.locales = {
            lang: flatten(json.loads((root / (lang + '.json')).read_text(encoding='utf-8'),
                                     object_pairs_hook=unique_object))
            for lang in ('en-US', 'ko-KR')}

    def test_same_leaf_keys_as_reference_locale(self):
        self.assertEqual(set(self.locales['en-US']), set(self.locales['ko-KR']))

    def test_nonblank_reference_has_nonblank_korean_value(self):
        for key, source in self.locales['en-US'].items():
            with self.subTest(key=key):
                target = self.locales['ko-KR'][key]
                self.assertIsInstance(target, str)
                if source.strip():
                    self.assertTrue(target.strip())

    def test_braced_placeholders_are_preserved(self):
        for key, source in self.locales['en-US'].items():
            with self.subTest(key=key):
                self.assertEqual(sorted(re.findall(r'\{[^{}]+\}', source)),
                                 sorted(re.findall(r'\{[^{}]+\}', self.locales['ko-KR'][key])))


if __name__ == '__main__':
    unittest.main()
