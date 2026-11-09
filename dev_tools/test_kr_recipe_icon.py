import unittest
import numpy as np
from types import SimpleNamespace
from unittest.mock import Mock, patch
import module.island_handler.korean_recipe_icon as icons
from module.base.utils import load_image
from module.island_handler.korean_recipe_icon import KoreanRecipeIconVerifier, label_supports_icon


class RecipeIconTest(unittest.TestCase):
    def test_independent_icon_and_long_visible_text_agree(self):
        verifier = KoreanRecipeIconVerifier()
        for key,row,text,item in [('601_9061',1,'기버섯 닭고기 스프',4010),
                                  ('604_9091',1,'게운 당근 계란말이',3033),
                                  ('604_9091',2,'행버그덮밥',3034)]:
            icon = load_image('dev_tools/fixtures/kr_recipe_%s_%s_icon.png' % (key,row))
            self.assertEqual(verifier.confirm(icon,text,{item}), item)
            self.assertIsNone(verifier.confirm(icon,text,{999}))
            self.assertIsNone(verifier.confirm(icon,'다른 제품', {item}))

    def test_known_other_name_and_short_generic_words_cannot_be_overridden(self):
        self.assertFalse(label_supports_icon('송이버섯 닭고기 스프','닭고기',set()))
        self.assertFalse(label_supports_icon('송이버섯 닭고기 스프','닭고기 스프',{'닭고기 스프'}))
        self.assertFalse(label_supports_icon('햄버그 덮밥','',set()))
        self.assertFalse(label_supports_icon('두부','두부',{'두부'}))

    def test_blank_wrong_shape_and_contradictory_icon_are_rejected(self):
        verifier = KoreanRecipeIconVerifier()
        self.assertIsNone(verifier.confirm(np.full((95,95,3),255,np.uint8),'행버그덮밥',{3034}))
        self.assertIsNone(verifier.confirm(np.zeros((74,95,3),np.uint8),'행버그덮밥',{3034}))
        icon = load_image('dev_tools/fixtures/kr_recipe_601_9061_1_icon.png')
        self.assertIsNone(verifier.confirm(icon,'행버그덮밥',{3034,4010}))

    def test_slot_mapping_cannot_relabel_other_facility_or_known_rows(self):
        image = load_image('dev_tools/fixtures/kr_recipe_601_9061_1_icon.png')
        self.assertEqual(icons.resolve_recipe_icons(['기버섯 닭고기 스프'],[None],[image],9061),[9900004])
        self.assertEqual(icons.resolve_recipe_icons(['기버섯 닭고기 스프'],[None],[image],9091),[None])
        self.assertEqual(icons.resolve_recipe_icons(['두부'],[601002],[image],9061),[601002])

    def test_live_name_path_requires_two_stable_cross_checks_without_input(self):
        import module.config.server as server
        import module.island_handler.recipe as recipe
        icon = load_image('dev_tools/fixtures/kr_recipe_601_9061_1_icon.png')
        grid = Mock()
        grid.crop.side_effect = lambda area, **kw: SimpleNamespace(buttons=[
            SimpleNamespace(area=(0,0,95,95) if area == (20,20,115,115) else (0,0,146,31))])
        ui = SimpleNamespace(recipe_grid=grid, get_recipe_grid=lambda:grid,
                             image_crop=lambda area, **kw:icon, working_slot_id=9061,
                             device=Mock(), is_in_recipe_menu=lambda:True)
        with patch.object(server,'server','kr'), patch.object(recipe,'RECIPE_PRODUCT_NAME_OCR') as ocr:
            ocr.ocr.return_value = ['기버섯 닭고기 스프']
            self.assertEqual(recipe.IslandRecipe.get_recipe_ids(ui),[9900004])
        self.assertEqual(ui.device.screenshot.call_count,2)
        ui.device.click.assert_not_called()
        ui.device.drag.assert_not_called()
