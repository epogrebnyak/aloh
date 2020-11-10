import warnings
from dataclasses import dataclass
from enum import Enum
from random import choice, uniform
from typing import List

import pandas as pd

warnings.simplefilter("ignore")


class Product(Enum):
    A = "H"
    B = "H10"
    C = "TA-HSA-10"
    D = "TA-240"


@dataclass
class Order:
    product: Product
    day: int
    volume: float
    price: float


def generate_between(a, b):
    return uniform(a, b)


def generate_day(n_days: int) -> int:
    # Может пропускать какой-то день на маленьких выборках
    return choice(range(n_days))


def rounds(x, f=1):
    """Округление, обычно до 5 или 10."""
    return round(x / f, 0) * f


@dataclass
class Size:
    min_order: float
    max_order: float
    rounding_factor: float = 1.0

    def generate(self):
        x = generate_between(self.min_order, self.max_order)
        return rounds(x, self.rounding_factor)


@dataclass
class Price:
    mean: float
    delta: float

    def generate(self):
        return uniform(self.mean - self.delta, self.mean + self.delta)


def volumes(total: float, size: Size) -> List[float]:
    xs = []
    rem = total
    while rem >= 0:
        x = size.generate()
        rem = rem - x
        if rem >= 0:
            xs.append(x)
        else:
            xs.append(total - sum(xs))
    return xs


def generate_orders(n_days, product, total_volume, size, price):
    for volume in volumes(total_volume, size):
        day = generate_day(n_days)
        price_ = price.generate()
        yield Order(product, day, volume, price_)


def to_dataframe(orders):
    n_days = max(r.day for r in orders) + 1
    df = pd.DataFrame(0, columns=[p.name for p in Product], index=range(n_days))
    for order in orders:
        df.loc[order.day, order.product.name] += order.volume
    return df


orders = list(
    generate_orders(
        n_days=7,
        product=Product.A,
        total_volume=3500,
        size=Size(min_order=50, max_order=120, rounding_factor=10),
        price=Price(mean=750, delta=75),
    )
)

df = to_dataframe(orders)
print(df)

assert df.A.sum() == 3500
