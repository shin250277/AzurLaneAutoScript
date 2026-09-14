"""Add verified KR localization to an existing generated island data file.

Usage: python -m dev_tools.island_kr_extractor SOURCE_FOLDER --revision SHA
Run the normal island extractor first when updating other regions. This pass
refuses changed shared mechanics instead of silently using another server's
numbers. Lua is parsed as literals, never executed. Without --write this is
an audit only; no game or account configuration is accessed.
"""
import argparse
import ast
import re
from pathlib import Path

from dev_tools.island_extractor import (
    IslandItem, IslandRecipe, dates_within_24_hours, island_time_to_sql_time,
)
from dev_tools.utils import LuaLoader


def merge_entry(row, mechanics, name=None):
    for key, value in mechanics.items():
        if key not in ('name', 'start_time', 'end_time') and row[key] != value:
            raise ValueError('KR shared mechanics differ: {}'.format(key))
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Missing Korean name')
        row['name']['kr'] = name.strip()


def merge_time(row, time, timer=False):
    if time == 'always':
        start = end = None if timer else 'always'
    elif time == 'stop':
        start = end = None
    else:
        offset = 1 if timer else 0
        if timer and time[0] != 'timer':
            raise ValueError('Unsupported Korean activity time')
        start = island_time_to_sql_time(time[offset])
        end = island_time_to_sql_time(time[offset + 1])
    row['start_time']['kr'] = start
    row['end_time']['kr'] = end


def extract(source, destination):
    tree = ast.parse(destination.read_text(encoding='utf-8'))
    tables = {node.targets[0].id: ast.literal_eval(node.value)
              for node in tree.body if isinstance(node, ast.Assign)}
    loader = LuaLoader(str(source), server='KR')
    cache = {}

    def load(name):
        if name not in cache:
            cache[name] = loader.load('sharecfg/{}.lua'.format(name))
        return cache[name]

    def rows(table, source_name):
        data = load(source_name)
        for key, row in tables[table].items():
            if key not in data:
                raise ValueError('Missing KR {} ID {}'.format(source_name, key))
            yield key, row, data[key]

    items = load('island_item_data_template')
    for key, row in tables['DIC_ISLAND_ITEM'].items():
        if key == 0:  # Synthetic planner currency; no source item zero.
            row['name']['kr'] = '섬 개발 PT'
            continue
        raw = items[key]
        merge_entry(row, IslandItem(raw).encode(), raw['name'])
    for key, row, raw in rows('DIC_ISLAND_RECIPE', 'island_formula'):
        merge_entry(row, IslandRecipe(raw).encode()[key], raw['name'])
    commissions = load('island_production_commission')
    for key, row, raw in rows('DIC_ISLAND_PRODUCTION_PLACE', 'island_production_place'):
        slots = [commissions[i]['slot'] for i in raw['commission_slot'].values()]
        merge_entry(row, {'slot': slots}, raw['name'])
    for key, row, raw in rows('DIC_ISLAND_SHOP_RECIPE', 'island_shop_goods'):
        merge_entry(row, {
            'resource_consume': {raw['resource_consume'][1]: raw['resource_consume'][2]},
            'items': {v[1]: v[2] for v in raw['items'].values()},
        }, raw['goods_name'])
        merge_time(row, raw['time'])
    for key, row, raw in rows('DIC_ISLAND_SHOP', 'island_shop_template'):
        merge_entry(row, {'goods': list(raw['goods_id'].values())
                         if isinstance(raw['goods_id'], dict) else []}, raw['tag_icon'][0])
    targets = load('island_task_target')
    for key, row, raw in rows('DIC_ISLAND_TASK', 'island_task'):
        target_id = raw['target_id'][0]
        target = targets[target_id]
        result = ({target['target_param'][0]: target['target_num']}
                  if isinstance(target['target_param'], dict) else {})
        merge_entry(row, {'target_id': target_id, 'target': result}, raw['name'])
        merge_time(row, raw['unlock_time'])
    for key, row, raw in rows('DIC_ISLAND_ACTIVITY', 'activity_template'):
        merge_time(row, raw['time'], timer=True)
    for key, row, raw in rows('DIC_ISLAND_SEASON', 'island_season'):
        merge_entry(row, {'task_list': list(raw['task_list'].values())})
        merge_time(row, raw['time'])
        activities = [i for i, activity in tables['DIC_ISLAND_ACTIVITY'].items()
                      if dates_within_24_hours(row['start_time']['kr'], activity['start_time']['kr'])
                      and dates_within_24_hours(row['end_time']['kr'], activity['end_time']['kr'])]
        # Expired KR activities can be explicitly 'stop', and must not inherit
        # the Chinese season's activity list merely because season IDs agree.
        row.setdefault('activity_by_server', {})['kr'] = activities
    return tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--destination', type=Path, default=Path('module/island/data.py'))
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.revision):
        parser.error('Use a full pinned source revision')
    tables = extract(args.source, args.destination)
    print('Verified Korean localization and schedules; shared mechanics preserved.')
    if not args.write:
        return
    lines = ['# This file was automatically generated by dev_tools/island_extractor.py',
             "# Don't modify it manually.",
             '# KR pass: python -m dev_tools.island_kr_extractor SOURCE --revision SHA --write',
             '# KR source: https://github.com/AzurLaneTools/AzurLaneLuaScripts/tree/{}/KR'.format(args.revision), '']
    for name, data in tables.items():
        lines.append(name + ' = {')
        lines.extend('    {!r}: {!r},'.format(key, value) for key, value in data.items())
        lines.extend(['}', ''])
    args.destination.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
