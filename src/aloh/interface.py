from typing import Dict, List, Union

from generate import Order


def max_day(orders: List[Order]):
    return max([order.day for order in orders])


def product(
    capacity: float,
    unit_cost: float,
    orders=List[Order],
    storage_days: Union[int, None] = None,
    requires: Dict[str, float] = {},
):
    if storage_days is None:
        storage_days = max_day(orders)
    return dict(
        capacity=capacity,
        unit_cost=unit_cost,
        orders=orders,
        storage_days=storage_days,
        requires=requires,
    )


def pick(ps: Dict, key: str):
    return {k: v[key] for k, v in ps.items()}


def n_days(ps: Dict):
    return max([max_day(ps[key]["orders"]) for key in ps.keys()]) + 1


ps = dict()
ps["A"] = product(capacity=100, unit_cost=10, orders=[Order(5, 100, 13)])
ps["B"] = product(capacity=50, unit_cost=15, storage_days=3, orders=[Order(1, 50, 17)])

assert pick(ps, "capacity") == {"A": 100, "B": 50}
assert pick(ps, "unit_cost") == {"A": 10, "B": 15}
assert pick(ps, "storage_days") == {"A": 5, "B": 3}
kwarg = dict(capacity=10, unit_cost=0.8, orders=[Order(0, 10, 1)])
assert product(**kwarg)["storage_days"] == 0
