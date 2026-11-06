import copy
import unittest
from unittest.mock import patch
from dev_tools.kr_planner_readonly import analyze
from module.island_handler.restaurant_config import RESTAURANT_CONFIG
import module.config.server as server


class ReadOnlyPlannerTest(unittest.TestCase):
    def config(self):
        restaurant = {}
        for data in RESTAURANT_CONFIG.values():
            restaurant[data['grade_key']] = 'bronze'
            for key in data['waitress_keys']:
                restaurant[key] = 'none'
        return {
            'IslandProductionPlanner': {'Storage': {'Storage': {'IslandTechnologyStatus': {310101: True}}},
                                        'IslandProductionPlanner': {}},
            'IslandBusiness': {'IslandRestaurant': restaurant},
            'IslandProduction': {'IslandProduction': {'HardFloorItems': '2000: 100'}},
            'IslandSeasonTask': {'IslandSeasonTask': {'TaskTarget': '2001: 12'}},
            'IslandOrder': {'IslandOrder': {'StuckSeasonOrderId': 0}}}

    def test_preserves_config_and_passes_protections_without_export(self):
        config = self.config()
        original = copy.deepcopy(config)
        original_server = server.server
        with patch('dev_tools.kr_planner_readonly.ProductionPlanCalculator') as factory:
            calc = factory.return_value
            calc.lp_success, calc.lp_status = True, 0
            calc.production_plan, calc.shop_plan, calc.exchange_plan = {}, {}, {}
            self.assertTrue(analyze(config)['success'])
            calc.solve_production_plan.assert_called_once_with(
                hard_floor_items={2000: 100}, task_target_items={2001: 12}, stuck_season_order_id=0)
            calc.restaurant_menus_to_yaml.assert_not_called()
        self.assertEqual(config, original)
        self.assertEqual(server.server, original_server)

    def test_missing_cache_does_not_scan_or_construct_planner(self):
        config = self.config()
        config['IslandProductionPlanner']['Storage'] = {}
        original_server = server.server
        with patch('dev_tools.kr_planner_readonly.ProductionPlanCalculator') as factory:
            with self.assertRaises(ValueError):
                analyze(config)
            factory.assert_not_called()
        self.assertEqual(server.server, original_server)
