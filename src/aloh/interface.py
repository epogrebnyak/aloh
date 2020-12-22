"""Interface to define inputs for the model. Use *Product* class."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aloh.requirements import Materials


@dataclass
class Order:
    """Order parameters."""

    day: int
    volume: float
    price: float


@dataclass
class Product:
    name: str
    capacity: float = 0
    unit_cost: Optional[float] = None
    storage_days: Optional[int] = None
    orders: List = field(default_factory=list)
    requires: Dict = field(default_factory=dict)

    def add_order(self, day: int, volume: float, price: float):
        x = dict(day=day, volume=volume, price=price)
        self.orders.append(x)

    def require(self, product: str, volume: float):
        self.requires[product] = volume


def names(products):
    return [p.name for p in products]


def capacities(products):
    return {p.name: p.capacity for p in products}


def unit_costs(products):
    return {p.name: p.unit_cost for p in products}


def storage_days(products, max_allowed_storage_days: int):
    sub = lambda x: x if (x is not None) else max_allowed_storage_days
    return {p.name: sub(p.storage_days) for p in products}


def order_dict(products):
    return {p.name: [Order(**abc) for abc in p.orders] for p in products}


def _max_day(order_dict):
    return max([order.day for orders in order_dict.values() for order in orders])


def _n_days(order_dict):
    return 1 + _max_day(order_dict)


def days(order_dict):
    return list(range(_n_days(order_dict)))


def get_materials(products):
    ms = Materials(names(products))
    print(ms.B)
    for p in products:
        for k, v in p.requires.items():
            ms.require(p_i=p.name, x=v, p_j=k)
    return ms
