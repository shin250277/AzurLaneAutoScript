"""KR asset preference and explicit JP fallback, without a game device."""
import unittest
from unittest.mock import patch

from module.base.resource import Resource
import module.config.server as server


class KoreanResourceSelectionTest(unittest.TestCase):
    def test_explicit_korean_value_wins_over_japanese_fallback(self):
        self.assertEqual(Resource.parse_property({'kr': 'korean', 'jp': 'japanese'}, s='kr'), 'korean')

    def test_missing_korean_uses_configured_japanese_value(self):
        self.assertEqual(Resource.parse_property({'jp': 'japanese', 'cn': 'chinese'}, s='kr'), 'japanese')

    def test_missing_fallback_is_not_guessed_from_other_server(self):
        with self.assertRaises(KeyError):
            Resource.parse_property({'cn': 'chinese'}, s='kr')

    def test_default_selection_follows_active_server(self):
        values = {'kr': 'korean', 'jp': 'japanese'}
        with patch.object(server, 'server', 'kr'):
            self.assertEqual(Resource.parse_property(values), 'korean')
        with patch.object(server, 'server', 'jp'):
            self.assertEqual(Resource.parse_property(values), 'japanese')

    def test_shared_value_is_not_reinterpreted(self):
        value = (1, 2, 3, 4)
        self.assertEqual(Resource.parse_property(value, s='kr'), value)


if __name__ == '__main__':
    unittest.main()
