import copy
import unittest

from dev_tools.island_kr_season_update import update
from module.island.data import DIC_ISLAND_ITEM, DIC_ISLAND_SEASON, DIC_ISLAND_TASK


class SeasonUpdateTest(unittest.TestCase):
    def fixture(self):
        tables = {'DIC_ISLAND_ITEM': {10: {}}, 'DIC_ISLAND_TASK': {}, 'DIC_ISLAND_SEASON': {}}
        season = {'task_list': {0: 100}, 'time': {0: {0: {0: 2026, 1: 11, 2: 19}, 1: {0: 0, 1: 0, 2: 0}},
                                                1: {0: {0: 2027, 1: 2, 2: 17}, 1: {0: 12, 1: 0, 2: 0}}}}
        tasks = {100: {'name': '차 비축', 'target_id': {0: 200}, 'unlock_time': 'always'}}
        targets = {200: {'target_param': {0: 10}, 'target_num': 500}}
        return tables, season, tasks, targets

    def test_addition_is_kr_only_and_does_not_mutate_input(self):
        tables, season, tasks, targets = self.fixture()
        before = copy.deepcopy(tables)
        result = update(tables, 5, season, tasks, targets)
        self.assertEqual(tables, before)
        self.assertEqual(result['DIC_ISLAND_SEASON'][5]['start_time'], {'kr': '2026-11-19 00:00:00'})
        self.assertEqual(result['DIC_ISLAND_TASK'][100]['target'], {10: 500})

    def test_unknown_target_fails_closed(self):
        tables, season, tasks, targets = self.fixture()
        targets[200]['target_param'][0] = 99
        with self.assertRaises(ValueError):
            update(tables, 5, season, tasks, targets)

    def test_shared_mechanics_cannot_be_overwritten(self):
        tables, season, tasks, targets = self.fixture()
        tables['DIC_ISLAND_TASK'][100] = {'target_id': 200, 'target': {10: 1}}
        with self.assertRaises(ValueError):
            update(tables, 5, season, tasks, targets)

    def test_pinned_winter_season_is_complete(self):
        season = DIC_ISLAND_SEASON[5]
        self.assertEqual(season['end_time']['kr'], '2027-02-17 12:00:00')
        self.assertEqual(season['task_list'], list(range(80001501, 80001531)))
        for task_id in season['task_list']:
            task = DIC_ISLAND_TASK[task_id]
            self.assertTrue(task['name']['kr'])
            self.assertTrue(set(task['target']).issubset(DIC_ISLAND_ITEM))
        self.assertEqual(DIC_ISLAND_TASK[80001501]['target'], {2014: 500})
        self.assertEqual(DIC_ISLAND_TASK[80001530]['target'], {})

    def test_winter_seeds_are_coin_only_and_locatable(self):
        from module.island.data import (DIC_ISLAND_SHOP_RECIPE, DIC_ISLAND_SHOP,
                                        DIC_ISLAND_SHOP_ITEM_TO_RECIPE)
        for item, goods, price in ((4048, 411029, 160), (4050, 411030, 80)):
            self.assertEqual(DIC_ISLAND_SHOP_ITEM_TO_RECIPE[item], goods)
            row = DIC_ISLAND_SHOP_RECIPE[goods]
            self.assertEqual(row['resource_consume'], {1: price})
            self.assertEqual(row['items'], {item: 1})
            self.assertEqual(row['servers'], ['kr'])
            self.assertTrue(any(goods in shop['goods'] for shop in DIC_ISLAND_SHOP.values()))

    def test_all_eight_winter_recipes_keep_source_costs_and_facility_links(self):
        from module.island.data import DIC_ISLAND_RECIPE, DIC_ISLAND_SLOT
        # Public KR island_formula/island_production_slot at pinned 0e0717b8.
        # These are data contracts, not eight completed production cycles.
        rows = [
            (9900025, 4047, 501, {4048: 4}, 8, 5, 90000),
            (9900026, 4049, 501, {4050: 4}, 12, 9, 30000),
            (9900027, 4051, 601, {4045: 2, 2602: 1}, 1, 12, 24000),
            (9900028, 4052, 601, {4049: 2, 2002: 5}, 1, 12, 9000),
            (9900029, 4053, 603, {4046: 2}, 1, 12, 12000),
            (9900030, 4054, 603, {4047: 2, 3004: 3}, 1, 12, 12000),
            (9900031, 4055, 706, {4043: 3}, 1, 6, 48000),
            (9900032, 4056, 706, {4043: 1, 4044: 4}, 1, 12, 6000),
        ]
        for code, item, place, cost, count, limit, workload in rows:
            with self.subTest(recipe=code):
                recipe = DIC_ISLAND_RECIPE[code]
                self.assertEqual(recipe['commission_cost'], cost)
                self.assertEqual(recipe['commission_product'], {item: count})
                self.assertEqual(recipe['production_limit'], limit)
                self.assertEqual(recipe['workload'], workload)
                self.assertTrue(recipe['name']['kr'])
                linked = [slot for slot in DIC_ISLAND_SLOT.values() if code in slot['activity_formula']]
                self.assertTrue(linked)
                self.assertEqual({slot['place'] for slot in linked}, {place})


if __name__ == '__main__':
    unittest.main()
