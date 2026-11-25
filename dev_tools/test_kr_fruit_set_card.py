import unittest
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier

class FruitSetCardTest(unittest.TestCase):
    def test_artwork_and_read_syllables_agree(self):
        frame = load_image('dev_tools/fixtures/kr_fruit_set_card.png')
        verifier = KoreanRecipeIconVerifier()
        self.assertEqual(verifier.confirm(frame, '퍜기로운 과일 세트', {3103: []}), 3103)
        self.assertIsNone(verifier.confirm(frame, '', {3103: []}))
        self.assertIsNone(verifier.confirm(frame, '레몬 새우', {3103: []}))
