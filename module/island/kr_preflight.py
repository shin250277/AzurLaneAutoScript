"""Pure, fail-closed checks used before Korean production can spend items."""
from numbers import Integral


def validate_recipe_counters(cost, amount, counters, require_available=True):
    """Require complete one-to-one evidence, not a silently truncated zip.

    Counter order follows the recipe ingredient grid. This validates quantities,
    not ingredient icons or permission to spend; callers must still enforce
    reserves, targets, selected recipe and dispatch limits.
    """
    if isinstance(amount, bool) or not isinstance(amount, Integral) or amount <= 0:
        return False
    if not cost or counters is None or len(counters) != len(cost):
        return False
    for unit_cost, counter in zip(cost.values(), counters):
        if not isinstance(counter, (list, tuple)) or len(counter) != 3:
            return False
        if any(isinstance(v, bool) or not isinstance(v, Integral) for v in counter):
            return False
        stock, required, remaining = counter
        if unit_cost <= 0 or required != unit_cost * amount:
            return False
        if stock < 0 or (require_available and stock < required) or remaining != stock - required:
            return False
    return True
