"""Pure, fail-closed checks used before Korean production can spend items."""
from numbers import Integral


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
