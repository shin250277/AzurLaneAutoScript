import unittest
import subprocess
import sys
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class IslandProductionNamesTest(unittest.TestCase):
    def test_recipe_probe_rejects_missing_or_invalid_counters(self):
        probe = method('module/island/production.py', 'IslandProduction', 'probe_korean_recipe_counters')
        ui = Mock()
        ui.set_recipe.return_value = True
        for counters in (None, [], [(0, 0, 0)]):
            ui.get_recipe_ingredient_counters.return_value = counters
            with self.assertRaises(TaskStopped):
                probe(ui, {101001: 790})
        ui.run_recipe.assert_not_called()
        ui.prepare_ingredients.assert_not_called()

    def test_recipe_probe_selects_and_reads_without_starting(self):
        probe = method('module/island/production.py', 'IslandProduction', 'probe_korean_recipe_counters')
        ui = Mock()
        ui.set_recipe.return_value = True
        ui.get_recipe_ingredient_counters.return_value = [(0, 9, -9)]
        result = probe(ui, {101001: 790, 101002: 800})
        self.assertEqual(set(result), {101001, 101002})
        self.assertEqual(ui.set_recipe.call_count, 2)
        ui.run_recipe.assert_not_called()
        ui.prepare_ingredients.assert_not_called()

    def test_korean_empty_field_runs_read_only_recipe_probe(self):
        dispatch = method('module/island/production.py', 'IslandProduction', 'dispatch_all',
                          DIC_ISLAND_PRODUCTION_PLACE={101: {'slot': [9001]}})
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.slot_grids = {101: Mock(buttons=['slot'])}
        ui.is_slot_empty.return_value = True
        ui.dispatch_slot.side_effect = TaskStopped('Read-only recipe probe')
        with self.assertRaises(TaskStopped):
            dispatch(ui)
        ui.dispatch_slot.assert_called_once_with(9001, 'slot')
        ui.dispatch_place.assert_not_called()

    def test_empty_korean_menu_does_not_choose_staff_or_start(self):
        run = method('module/island_handler/restaurant.py', 'IslandRestaurant', 'run',
                     KR_RESTAURANT_EMPTY=Mock())
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.restaurant_running.return_value = False
        ui.restaurant_resting.return_value = False
        ui.is_korean_menu_empty.return_value = True
        self.assertFalse(run(ui))
        ui.choose_waitress.assert_not_called()
        ui.select_dishes.assert_not_called()
        ui.restaurant_start.assert_not_called()

    def test_unrecognized_korean_restaurant_is_not_silently_skipped(self):
        templates = {name: Mock() for name in ('TEMPLATE_ISLAND_BUSINESS_KOI',
                     'TEMPLATE_ISLAND_BUSINESS_BEAR', 'TEMPLATE_ISLAND_BUSINESS_EATERY',
                     'TEMPLATE_ISLAND_BUSINESS_GRILL', 'TEMPLATE_ISLAND_BUSINESS_CAFE')}
        for template in templates.values():
            template.match.return_value = False
        detect = method('module/island/business.py', 'IslandBusiness', 'get_restaurant_id', **templates)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.return_value = range(1)
        with self.assertRaises(TaskStopped):
            detect(ui, 'restaurant')
        ui.device.image_save.assert_called_once()

    def test_korean_dispatch_stops_before_unvalidated_recipe_ocr(self):
        dispatch = method('module/island/production.py', 'IslandProduction', 'dispatch_all')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.slot_grids = {}
        ui.next_page.return_value = False
        with self.assertRaises(TaskStopped):
            dispatch(ui)
        ui.ensure_top_page.assert_not_called()
        ui.dispatch_place.assert_not_called()

    def test_empty_slot_cannot_be_finished_even_with_white_pixels(self):
        finished = method('module/island/production.py', 'IslandProduction', 'is_slot_finished',
                          Button=object, TICK_AREA=(30, 35, 52, 51))
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.is_slot_empty.return_value = True
        ui.image_color_count.return_value = True
        self.assertFalse(finished(ui, Mock(name='slot')))
        ui.is_slot_empty.return_value = False
        self.assertTrue(finished(ui, Mock(name='slot')))

    def test_korean_labels_are_distinct_and_registered(self):
        code = '''
import numpy as np
import module.config.server as server
server.server = 'kr'
from module.island import assets
names = ['FIELD','RANCH','FISHERY','MINE','WOOD','ORCHARD','NURSERY','KOI',
         'BEAR','EATERY','GRILL','LUMBER','MACHINERY','ELECTRONIC','CRAFTS','CAFE']
templates = [getattr(assets, 'TEMPLATE_ISLAND_PRODUCTION_' + name) for name in names]
for template in templates:
    assert '/kr/' in template.file.replace('\\\\', '/')
    assert template.match(template.image)
    blank = np.zeros((39, 265, 3), dtype=np.uint8)
    assert not template.match(blank)
    for other in templates:
        if other is template:
            continue
        candidate = blank.copy()
        h, w = other.image.shape[:2]
        candidate[:h, :w] = other.image
        assert not template.match(candidate), (template.name, other.name)
button = assets.ISLAND_PRODUCTION_RECEIVE
assert '/kr/' in button.file.replace('\\\\', '/')
for name in ['KOI', 'BEAR', 'EATERY', 'GRILL', 'CAFE']:
    template = getattr(assets, 'TEMPLATE_ISLAND_BUSINESS_' + name)
    assert '/kr/' in template.file.replace('\\\\', '/')
    assert template.match(template.image)
    assert not template.match(np.zeros((60, 265, 3), dtype=np.uint8))
from module.island_handler.assets import ISLAND_RESTAURANT_CHECK
assert '/kr/' in ISLAND_RESTAURANT_CHECK.file.replace('\\\\', '/')
from module.base.template import Template
empty = Template('./assets/kr/island_handler/KR_RESTAURANT_EMPTY.png')
assert empty.match(empty.image)
assert not empty.match(np.zeros((230, 500, 3), dtype=np.uint8))
'''
        result = subprocess.run([sys.executable, '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_unchanged_finished_slot_is_not_reported_as_claimed(self):
        claim = method('module/island/production.py', 'IslandProduction', 'claim_slot_reward',
                       ISLAND_PRODUCTION_RECEIVE='receive', ISLAND_PRODUCTION_SELECT_CHARACTER='character',
                       ISLAND_PRODUCTION_RERUN='rerun', ISLAND_CLICK_SAFE_AREA='safe',
                       page_island_manage=Mock(check_button='manage'), Button=object)
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.loop.side_effect = [range(1), range(1)]
        ui.is_slot_finished.return_value = True
        ui.handle_island_additional.return_value = False
        ui.appear_then_click.return_value = False
        ui.ui_page_appear.return_value = False
        ui.is_enter_window_shown.return_value = False
        ui.appear.return_value = False
        ui.match_template_color.return_value = True
        with self.assertRaises(TaskStopped):
            claim(ui, 'slot')
        ui.device.image_save.assert_called_once()

    def test_unrecognized_korean_places_stop_before_swiping(self):
        check = method('module/island/production.py', 'IslandProduction', '_check_kr_production_names')
        ui = Mock()
        ui.config.SERVER = 'kr'
        for names in ([], [None] * 6, [101, None]):
            with self.assertRaises(TaskStopped):
                check(ui, names)
        ui.device.drag.assert_not_called()
        self.assertEqual(ui.device.image_save.call_count, 3)
        check(ui, [101, 102, 201])


if __name__ == '__main__':
    unittest.main()
