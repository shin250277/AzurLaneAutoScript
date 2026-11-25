"""Import a pinned KR season without inventing schedules for other regions.

Offline only: reads public Lua literals and generated data, never account config.
"""
import argparse
import ast
import copy
import re
from pathlib import Path

from dev_tools.island_kr_extractor import merge_time
from dev_tools.island_extractor import IslandRecipeExtractor, IslandSeasonRequestExtractor, dates_within_24_hours
from dev_tools.utils import LuaLoader


def update(tables, season_id, season, tasks, targets):
    result = copy.deepcopy(tables)
    ids = list(season['task_list'].values())
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Empty or duplicate season task list')
    for task_id in ids:
        raw = tasks[task_id]
        target_id = raw['target_id'][0]
        target = targets[target_id]
        params = target['target_param']
        reservation = {params[0]: target['target_num']} if isinstance(params, dict) else {}
        if any(item not in result['DIC_ISLAND_ITEM'] or type(count) is not int or count <= 0
               for item, count in reservation.items()):
            raise ValueError('Unknown item or invalid target quantity')
        name = raw['name'].strip()
        if not name or '\ufffd' in name:
            raise ValueError('Invalid Korean task name')
        row = result['DIC_ISLAND_TASK'].setdefault(task_id, {
            'name': {}, 'target_id': target_id, 'target': reservation,
            'start_time': {}, 'end_time': {},
        })
        if row['target_id'] != target_id or row['target'] != reservation:
            raise ValueError('Existing shared task mechanics differ')
        row['name']['kr'] = name
        row['target_num'] = target['target_num']
        merge_time(row, raw['unlock_time'])
    row = result['DIC_ISLAND_SEASON'].setdefault(season_id, {
        'start_time': {}, 'end_time': {}, 'task_list': ids, 'activity': [],
    })
    if row['task_list'] != ids:
        raise ValueError('Existing shared season task list differs')
    merge_time(row, season['time'])
    # Activity/order data is not part of this import. Never inherit a foreign list.
    row.setdefault('activity_by_server', {}).setdefault('kr', [])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--season', required=True, type=int)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.revision):
        parser.error('A full pinned revision is required')
    destination = Path('module/island/data.py')
    original = destination.read_text(encoding='utf-8')
    tree = ast.parse(original)
    tables = {node.targets[0].id: ast.literal_eval(node.value)
              for node in tree.body if isinstance(node, ast.Assign)}
    loader = LuaLoader(str(args.source), server='KR')
    for key, raw in loader.load('sharecfg/island_item_data_template.lua').items():
        if isinstance(key, int) and 1000 <= key <= 100000 and key not in tables['DIC_ISLAND_ITEM']:
            row = {field: raw[field] for field in ('pt_num', 'manage_influence', 'order_price')}
            row['name'] = {}
            row['name']['kr'] = raw['name']
            tables['DIC_ISLAND_ITEM'][key] = row
    result = update(tables, args.season,
                    loader.load('sharecfg/island_season.lua')[args.season],
                    loader.load('sharecfg/island_task.lua'),
                    loader.load('sharecfg/island_task_target.lua'))
    season = result['DIC_ISLAND_SEASON'][args.season]
    season['servers'] = ['kr']
    activities = []
    for key, raw in loader.load('sharecfg/activity_template.lua').items():
        if not isinstance(key, int) or raw['type'] not in (5001, 5002, 5003, 5004):
            continue
        row = {'type': raw['type'], 'start_time': {}, 'end_time': {},
               'config_data': list(raw['config_data'].values()) if isinstance(raw['config_data'], dict) else []}
        merge_time(row, raw['time'], timer=True)
        if (dates_within_24_hours(season['start_time']['kr'], row['start_time']['kr'])
                and dates_within_24_hours(season['end_time']['kr'], row['end_time']['kr'])):
            old = result['DIC_ISLAND_ACTIVITY'].get(key)
            if old is not None and old != row:
                raise ValueError('Activity already differs; use full KR merge')
            result['DIC_ISLAND_ACTIVITY'][key] = row
            activities.append(key)
    season['activity_by_server']['kr'] = activities
    for key, raw in loader.load('sharecfg/island_order.lua').items():
        if isinstance(key, int) and raw['activity_id'] in activities:
            row = IslandSeasonRequestExtractor.extract_order(raw)
            if not set(row['request']).issubset(result['DIC_ISLAND_ITEM']):
                raise ValueError('Unknown season order item')
            result['DIC_ISLAND_SEASON_ORDER'][key] = row
    for key, raw in loader.load('sharecfg/island_formula.lua').items():
        if (isinstance(key, int) and key not in result['DIC_ISLAND_RECIPE']
                and raw['attribute'] in (1, 2, 3, 4, 6) and (key // 10000 < 700 or key // 10000 >= 990)):
            row = IslandRecipeExtractor.extract_recipe(raw)
            row['name']['kr'] = raw['name']
            if not (set(row['commission_product']) | set(row['commission_cost'])).issubset(result['DIC_ISLAND_ITEM']):
                raise ValueError('Unknown recipe item')
            result['DIC_ISLAND_RECIPE'][key] = row
    for key, raw in loader.load('sharecfg/island_production_slot.lua').items():
        if key in result['DIC_ISLAND_SLOT']:
            row = dict(attribute=raw['attribute'], place=raw['place'], formula=list(raw['formula'].values()),
                       activity_formula=[recipe for pair in raw['activity_formula'].values()
                                         for recipe in pair[1].values()])
            old = result['DIC_ISLAND_SLOT'][key]
            if any(row[field] != old[field] for field in ('attribute', 'place', 'formula')):
                raise ValueError('Non-season production slot changed')
            old['activity_formula'] = row['activity_formula']
    # Import only new coin-priced materials needed by the seasonal recipes.
    needed = set()
    for activity in activities:
        if result['DIC_ISLAND_ACTIVITY'][activity]['type'] == 5004:
            for recipe_id in result['DIC_ISLAND_ACTIVITY'][activity]['config_data']:
                needed.update(result['DIC_ISLAND_RECIPE'][recipe_id]['commission_cost'])
    new_goods = set()
    for key, raw in loader.load('sharecfg/island_shop_goods.lua').items():
        if not isinstance(key, int) or not 100000 <= key < 412000:
            continue
        items = {value[1]: value[2] for value in raw['items'].values()}
        if key in result['DIC_ISLAND_SHOP_RECIPE'] or not set(items).intersection(needed):
            continue
        cost = raw['resource_consume']
        if raw['pay_id'] or cost[0] != 41 or cost[1] != 1 or cost[2] <= 0:
            raise ValueError('Season material is not an ordinary island-coin purchase')
        row = {'name': {'kr': raw['goods_name']}, 'resource_consume': {1: cost[2]},
               'items': items, 'start_time': {}, 'end_time': {}, 'servers': ['kr']}
        merge_time(row, raw['time'])
        result['DIC_ISLAND_SHOP_RECIPE'][key] = row
        for item in items:
            result['DIC_ISLAND_SHOP_ITEM_TO_RECIPE'][item] = key
        new_goods.add(key)
    for key, raw in loader.load('sharecfg/island_shop_template.lua').items():
        if key in result['DIC_ISLAND_SHOP']:
            source = {'goods': list(raw['goods_id'].values()) if isinstance(raw['goods_id'], dict) else []}
            old = result['DIC_ISLAND_SHOP'][key]
            for goods in source['goods']:
                if goods in new_goods and goods not in old['goods']:
                    old['goods'].append(goods)
    if args.write:
        lines = original.splitlines()
        for node in reversed(tree.body):
            if isinstance(node, ast.Assign) and node.targets[0].id in (
                    'DIC_ISLAND_SEASON', 'DIC_ISLAND_TASK', 'DIC_ISLAND_ITEM',
                    'DIC_ISLAND_ACTIVITY', 'DIC_ISLAND_SEASON_ORDER', 'DIC_ISLAND_RECIPE', 'DIC_ISLAND_SLOT',
                    'DIC_ISLAND_SHOP_RECIPE', 'DIC_ISLAND_SHOP_ITEM_TO_RECIPE', 'DIC_ISLAND_SHOP'):
                name = node.targets[0].id
                end = node.lineno
                while lines[end] != '}':
                    end += 1
                lines[node.lineno - 1:end + 1] = [name + ' = {'] + [
                    '    {!r}: {!r},'.format(k, v) for k, v in result[name].items()] + ['}']
        lines = [line for line in lines if not line.startswith('# KR season {} source:'.format(args.season))]
        lines.insert(4, '# KR season {} source: https://github.com/AzurLaneTools/AzurLaneLuaScripts/tree/{}/KR'.format(args.season, args.revision))
        destination.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Verified KR season {}: {} tasks'.format(args.season, len(result['DIC_ISLAND_SEASON'][args.season]['task_list'])))


if __name__ == '__main__':
    main()
