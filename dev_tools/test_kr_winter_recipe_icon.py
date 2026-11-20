import unittest
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier


class WinterRecipeIconTest(unittest.TestCase):
    def test_artwork_requires_observed_specific_title_and_facility(self):
        verifier = KoreanRecipeIconVerifier()
        frame = load_image('assets/kr/island_recipe_icon/4051.png')
        self.assertEqual(verifier.confirm(frame, '표고버섯 닭고기', {4051, 4052}), 4051)
        for text in ('', '닭고기', '푸른 대추죽', '겨울 표고버섯'):
            self.assertIsNone(verifier.confirm(frame, text, {4051, 4052}))
        self.assertIsNone(verifier.confirm(frame, '표고버섯 닭고기', {4052}))


if __name__ == '__main__':
    unittest.main()
