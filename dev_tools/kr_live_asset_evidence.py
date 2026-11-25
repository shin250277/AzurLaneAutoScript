"""Summarize explicit clicks in completed KR scheduler tasks, never export raw logs.

This is evidence that ALAS used a named control. A coordinate click alone
does not establish a visual match or the success of a specific transaction.
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


SERVER = re.compile(r'\[Server\] (\w+)')
TASK = re.compile(r'Scheduler: (Start|End) task `(\w+)`')
CLICK = re.compile(r'\| INFO \| Click \(\s*\d+,\s*\d+\) @ ([A-Z][A-Z_0-9]*)\s*$')


def completed_clicks(lines):
    server = active = None
    clicks = set()
    invalid = False
    for line in lines:
        region = SERVER.search(line)
        if region:
            server = region.group(1)
            if active and server != 'kr':
                invalid = True
        task = TASK.search(line)
        if task:
            action, name = task.groups()
            if action == 'Start':
                active, clicks, invalid = name, set(), server != 'kr'
            else:
                if name == active and not invalid:
                    yield from clicks
                active = None
            continue
        if active:
            if '| ERROR |' in line or '| CRITICAL |' in line or 'Traceback (most recent call last)' in line:
                invalid = True
            click = CLICK.search(line)
            if click:
                clicks.add(click.group(1))


def report(log_dir, inventory, output):
    with inventory.open(encoding='utf-8') as src:
        assets = list(csv.DictReader(src))
    by_name = defaultdict(list)
    for row in assets:
        by_name[row['name']].append(row)
    dates = defaultdict(set)
    for path in sorted(log_dir.glob('????-??-??_alas.txt')):
        with path.open(encoding='utf-8', errors='replace') as src:
            for name in completed_clicks(src):
                if len(by_name.get(name, ())) == 1:
                    dates[name].add(path.name[:10])
    with output.open('w', newline='', encoding='utf-8') as dest:
        out = csv.writer(dest, lineterminator='\n')
        out.writerow(('module', 'name', 'first_observed', 'last_observed', 'distinct_days'))
        for name, days in sorted(dates.items()):
            out.writerow((by_name[name][0]['module'], name, min(days), max(days), len(days)))
    print(len(dates), 'unique named controls used in completed KR tasks')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('log_dir', 'inventory', 'output'):
        parser.add_argument(key, type=Path)
    report(**vars(parser.parse_args()))
