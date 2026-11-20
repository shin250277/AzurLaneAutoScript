"""Fail-closed, pure eligibility for the KR seasonal one-step submission.

KR IslandTaskHelper RECYCLE progress is GetInventoryAgency():GetOwnCount().
Counters must be captured twice by the caller; obtained cards are excluded.
"""
import re


PENDING_KEY = 'IslandSeasonTask.Storage.Storage.KoreanPendingClaim'


def claimable_tasks(progress, tasks, protected):
    """Return ready ids, [] for protected stock, None for invalid evidence."""
    if not isinstance(progress, dict) or not progress:
        return None
    if any(type(v) is not int or v < 0 for v in protected.values()):
        return None
    ready, costs, stocks = [], {}, {}
    for task_id, evidence in progress.items():
        task = tasks.get(task_id)
        if (not task or not isinstance(evidence, (tuple, list))
                or len(evidence) != 2 or type(evidence[1]) is not bool):
            return None
        counter, obtained = evidence
        match = re.fullmatch(r'(\d+)/(\d+)', counter) if isinstance(counter, str) else None
        if not match:
            return None
        current, total = map(int, match.groups())
        if type(task.get('target_num')) is not int or total <= 0 or total != task['target_num']:
            return None
        if obtained:
            continue
        target = task.get('target')
        if not isinstance(target, dict) or len(target) > 1:
            return None
        if target:
            item, count = next(iter(target.items()))
            if count != total or (item in stocks and stocks[item] != current):
                return None
            stocks[item] = current
        if current < total:
            continue
        ready.append(task_id)
        for item, amount in target.items():
            costs[item] = costs.get(item, 0) + amount
    if any(stocks[item] - cost < protected.get(item, 0) for item, cost in costs.items()):
        return []
    return ready
