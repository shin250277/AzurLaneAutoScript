"""Pure, fail-closed checks used before Korean production can spend items."""
from numbers import Integral


def verified_season_targets(task_ids, active_ids, tasks, items):
    """Validate a completed scan; None means preserve the existing plan.

    Caller must establish scan completeness and an unchanged active KR season.
    An empty verified scan may clear completed goals, never an unknown season.
    """
    if not active_ids or not isinstance(task_ids, (list, tuple)):
        return None
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v not in active_ids
           for v in task_ids) or len(set(task_ids)) != len(task_ids):
        return None
    result = {}
    for task_id in task_ids:
        target = tasks.get(task_id, {}).get('target')
        if not isinstance(target, dict):
            return None
        for item, amount in target.items():
            if (isinstance(item, bool) or not isinstance(item, Integral) or item not in items
                    or isinstance(amount, bool) or not isinstance(amount, Integral) or amount <= 0):
                return None
            result[item] = result.get(item, 0) + amount
    return result


def verified_owned_unit_cost(cost, counters, components=None):
    """One-batch displayed cost; an explicit surcharge is never inferred.

    This is not start permission. The caller still caps batches, reserves all
    protected stock and verifies the final scaled counters before any input.
    """
    if not cost:
        return {} if counters == [] else None
    if not validate_recipe_counters(cost, 1, counters, require_available=False,
                                    components=components):
        return None
    return {item: counter[1] for item, counter in zip(cost, counters)}


def owned_batch_limit(cost, counters, requested, production_limit, protected):
    """Finite batches from verified one-batch counters; never buy/exchange.

    Caller supplies the sum of hard floors, restaurant reservations, task
    reservations and any additional protected buffer for each ingredient.
    This is quantity validation, not permission to click the start button.
    """
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v <= 0
           for v in (requested, production_limit)):
        return 0
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v < 0
           for v in protected.values()):
        return 0
    limit = min(requested, production_limit)
    if not cost:
        return limit if counters == [] else 0
    if not validate_recipe_counters(cost, 1, counters):
        return 0
    for (item, unit), (stock, required, remaining) in zip(cost.items(), counters):
        limit = min(limit, max(stock - protected.get(item, 0), 0) // unit)
    return limit


def owned_start_verified(cost, counters, amount, protected):
    """Recheck the final displayed amount and balances immediately before start."""
    if isinstance(amount, bool) or not isinstance(amount, Integral) or amount <= 0:
        return False
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v < 0
           for v in protected.values()):
        return False
    if not cost:
        return counters == []
    if not validate_recipe_counters(cost, amount, counters):
        return False
    return all(counter[2] >= protected.get(item, 0)
               for item, counter in zip(cost, counters))


def verified_recipe_stocks(recipe_ids, stocks, previous):
    """Reject incomplete, duplicate or conflicting observations before planning."""
    if not recipe_ids or stocks is None or len(recipe_ids) != len(stocks):
        return None
    if any(isinstance(value, bool) or not isinstance(value, Integral) or value <= 0
           for value in recipe_ids) or len(set(recipe_ids)) != len(recipe_ids):
        return None
    if any(isinstance(value, bool) or not isinstance(value, Integral) or value < 0
           for value in stocks):
        return None
    page = dict(zip(recipe_ids, stocks))
    if any(key in previous and previous[key] != value for key, value in page.items()):
        return None
    return page


def validate_recipe_counters(cost, amount, counters, require_available=True, components=None):
    """Require complete one-to-one evidence, not a silently truncated zip.

    Counter order follows the recipe ingredient grid. This validates quantities,
    not ingredient icons or permission to spend; callers must still enforce
    reserves, targets, selected recipe and dispatch limits.
    """
    if isinstance(amount, bool) or not isinstance(amount, Integral) or amount <= 0:
        return False
    if not cost or counters is None or len(counters) != len(cost):
        return False
    for index, (unit_cost, counter) in enumerate(zip(cost.values(), counters)):
        if not isinstance(counter, (list, tuple)) or len(counter) != 3:
            return False
        if any(isinstance(v, bool) or not isinstance(v, Integral) for v in counter):
            return False
        stock, required, remaining = counter
        if unit_cost <= 0:
            return False
        if required != unit_cost * amount:
            # Read-only ranch audit: verify the displayed base + boost, not
            # an inferred multiplier. Spending retains the strict original gate.
            if require_available or not isinstance(components, (list, tuple)) or len(components) != len(cost):
                return False
            part = components[index]
            if not isinstance(part, (list, tuple)) or len(part) != 2:
                return False
            base, boost = part
            if (any(isinstance(v, bool) or not isinstance(v, Integral) for v in part)
                    or base != unit_cost * amount or boost < 0 or base + boost != required):
                return False
        if stock < 0 or (require_available and stock < required) or remaining != stock - required:
            return False
    return True
