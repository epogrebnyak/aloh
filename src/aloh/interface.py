from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Order:
    """Order parameters."""

    day: int
    volume: float
    price: float


VERY_LARGE_NUMBER = 10_000


class Commodity:
    name: str
    storage_days: int = VERY_LARGE_NUMBER


class Machine:
    capacity: float
    unit_cost: float


@dataclass
class Product:
    name: str
    capacity: float = 0
    unit_cost: Optional[float] = None
    storage_days: Optional[int] = None
    orders: List = field(default_factory=list)
    requires: Dict = field(default_factory=dict)

    def add_order(self, day: int, volume: float, price: float):
        self.orders.append(Order(day, volume, price))

    def require(self, product: str, volume: float):
        pass


@dataclass
class Dataset:
    product_names: List[str]
    capacities: Dict[str, float]
    unit_costs: Dict[str, float]
    storage_days: Dict[str, int]
    order_dict: Dict[str, List[Order]]

    @property
    def max_day(self):
        all_orders = [order for orders in self.order_dict.values() for order in orders]
        return max([order.day for order in all_orders])

    @property
    def n_days(self):
        return 1 + self.max_day

    @property
    def days(self):
        return list(range(self.n_days))


def make_dataset(products: List[Product]):
    product_names = [p.name for p in products]
    capacities = {p.name: p.capacity for p in products}
    unit_costs = {p.name: p.unit_cost for p in products}
    storage_days = {p.name: p.storage_days for p in products}
    order_dict = {p.name: p.orders for p in products}
    ds = Dataset(product_names, capacities, unit_costs, storage_days, order_dict)
    for k, v in ds.storage_days.items():
        if v is None:
            ds.storage_days[k] = ds.n_days - 1
    return ds
