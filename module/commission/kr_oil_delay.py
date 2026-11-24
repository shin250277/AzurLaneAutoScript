from time import monotonic


# A campaign's badge cannot distinguish a full oil store from a new reward.
# Keep the deferral scoped to this scheduler process and profile.
_deadline = {}


def defer(profile):
    _deadline[profile] = monotonic() + 30 * 60


def active(profile):
    return monotonic() < _deadline.get(profile, float('-inf'))
