"""Offline planner analysis from cached config; no device, export or game actions."""
import argparse
import json
from datetime import datetime
from pathlib import Path

import module.config.server as server
from module.config.utils import server_time_offset
from module.island.utils import load_hard_floor_items, load_item_mapping, load_technology_status
from module.island_handler.production_plan_calculator import ProductionPlanCalculator, get_current_activity_list
from module.island_handler.restaurant_config import RESTAURANT_CONFIG


def analyze(config):
    previous_server = server.server
    server.server = 'kr'
    try:
        return _analyze_cached(config)
    finally:
        server.server = previous_server


def _analyze_cached(config):
    planner = config['IslandProductionPlanner']
    cached = planner.get('Storage', {}).get('Storage', {}).get('IslandTechnologyStatus')
    if not cached:
        raise ValueError('No cached technology status; do not infer unlocks or start a device scan')
    options = planner['IslandProductionPlanner']
    restaurant = config['IslandBusiness']['IslandRestaurant']
    settings = {key: {'grade': restaurant[data['grade_key']],
                      'waitress_slots': [restaurant.get(field) for field in data['waitress_keys']]}
                for key, data in RESTAURANT_CONFIG.items()}
    calc = ProductionPlanCalculator(
        technology_status=load_technology_status(cached),
        activity_list=get_current_activity_list(datetime.now() - server_time_offset()),
        place_efficiency={101: options.get('FieldsEfficiency', 0),
                          501: options.get('OrchardEfficiency', 0),
                          502: options.get('NurseryEfficiency', 0)},
        restaurant_settings=settings,
        daily_profit_lower_limit=options.get('DailyProfitLowerLimit', 0),
        daily_buffer_safety_margin=options.get('DailyBufferSafetyMargin', 0))
    calc.solve_production_plan(
        hard_floor_items=load_hard_floor_items(config['IslandProduction']['IslandProduction']['HardFloorItems']),
        task_target_items=load_item_mapping(config['IslandSeasonTask']['IslandSeasonTask']['TaskTarget']),
        stuck_season_order_id=config['IslandOrder']['IslandOrder'].get('StuckSeasonOrderId', 0))
    return dict(success=bool(calc.lp_success), status=int(calc.lp_status),
                production_recipes=len(calc.production_plan), purchases=len(calc.shop_plan),
                exchanges=len(calc.exchange_plan),
                limitation='Cached technology and stored targets only; no config export or game actions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config/alas.json')
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(Path(args.config).read_text(encoding='utf-8'))), indent=2))
