"""Narrow visual resolution for observed KR homonymous order items."""
from module.base.template import Template
from module.island.data import DIC_ISLAND_ITEM


def resolve_order_icon(name, image, row):
    if not isinstance(name, str) or row not in (0, 1, 2):
        return None
    normalized = ''.join(name.split())
    candidates = [key for key, item in DIC_ISLAND_ITEM.items()
                  if normalized and ''.join(item['name'].get('kr', '').split()) == normalized]
    # KR calls both corn bait (1501) and harvested corn (2001) '옥수수'.
    # Only the observed harvested-corn icon is supported; bait stays blocked.
    if set(candidates) != {1501, 2001}:
        return None
    y = 253 + row * 79
    icon = image[y:y + 51, 900:951]
    if icon.shape[:2] != (51, 51):
        return None
    template = Template('./assets/kr/island/KR_ORDER_CORN.png')
    return 2001 if template.match(icon, similarity=0.95) else None
