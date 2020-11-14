import warnings
from dataclasses import dataclass
from enum import Enum
from random import choice, uniform
from typing import List

import pandas as pd
import pulp


LpExpression = pulp.pulp.LpAffineExpression


warnings.simplefilter("ignore")


class Product(Enum):
    A = "H"
    B = "H10"
    C = "TA-HSA-10"
    D = "TA-240"
    

def rounds(x, f=1):
    """Округление, обычно до 5 или 10."""
    return round(x / f, 0) * f


def days_list(n_days: int):
    return list(range(n_days))


@dataclass
class Price:
    mean: float
    delta: float

    def generate(self):
        p = uniform(self.mean - self.delta, self.mean + self.delta)
        return round(p, 1)

@dataclass
class Volume:
    min_order: float
    max_order: float
    rounding_factor: float = 1.0

    def generate(self) -> float:
        x = uniform(self.min_order, self.max_order)
        return rounds(x, self.rounding_factor)

def generate_volumes(total_volume: float, sizer: Volume)-> List[float]:
        xs = []
        remaining = total_volume
        while remaining >= 0:
            x = sizer.generate()
            remaining = remaining - x
            if remaining >= 0:
                xs.append(x)
            else:
                xs.append(total_volume - sum(xs))
        return xs

def generate_day(n_days: int) -> int:
    return choice(range(n_days))

@dataclass
class Order:
    day: int
    volume: float
    price: float


def generate_orders(n_days, total_volume, pricer, sizer):
    sim_volumes = generate_volumes(total_volume, sizer)
    n = len(sim_volumes)
    days = days_list(n_days)
    sim_days = [choice(days) for _ in range(n)]
    sim_prices = [pricer.generate() for _ in range(n)]
    return [Order(d, v, p) for (d, v, p) in zip(sim_days, sim_volumes, sim_prices)]


def demand(orders, days):
    dict_ = dict([(d,0) for d in days])
    for order in orders:
        dict_[order.day] += order.volume
    return dict_


def demand_dataframe(orders, n_days):
    df = pd.DataFrame(0, columns=['volume'], index=days_list(n_days))
    for order in orders:
        df.loc[order.day, 'volume'] += order.volume
    df.index.name = "day"
    return df

# end simulation
# start model


def sales(orders, accept) -> List[LpExpression]:
    return [order.volume * order.price * accept[i] for i, order in enumerate(orders)]


def accumulate(var, i) -> LpExpression:
    return pulp.lpSum([var[k] for k in range(i + 1)])


def peek(x):
    """
    Lookup into dict of pulp.LpVariable.
    """
    return [v.value() for v in x.values()]


class Model:
    obj = pulp.LpMaximize

    def __init__(self, name="Planning model", n_days=1, max_capacity=0):
        self.model = pulp.LpProblem(name, self.obj)
        self.days = days_list(n_days)
        self.production = pulp.LpVariable.dicts(
            "Production", self.days, lowBound=0, upBound=max_capacity
        )
        self.orders = []
        self.feasibility = None

    def add_orders(self, orders):
        self.orders = orders
        self.accept = pulp.LpVariable.dicts(
            "AcceptOrder", range(len(orders)), cat="Binary"
        )
        self.purchases = self.make_purchases(orders, self.days, self.accept)

    @staticmethod
    def make_purchases(orders, days, accept):
        """Purchases are accepted orders."""
        purchases = dict()
        for d in days:
            daily_orders = [
                order.volume * accept[i] for i, order in enumerate(orders) if d == order.day
            ]
            purchases[d] = pulp.lpSum(daily_orders)
        return purchases

    def set_closed_sum(self):
        self.model += pulp.lpSum(self.production) == pulp.lpSum(self.purchases)

    def set_objective(self):
        self.model += pulp.lpSum(sales(self.orders, self.accept))

    def set_non_zero_inventory(self):
        self.inventory = dict()
        for d in self.days:
            self.inventory[d] = accumulate(self.production, d) - accumulate(
                self.purchases, d
            )
            self.model += self.inventory[d] >= 0, f"Positive inventory at day {d}"

    def solve(self):
        self.feasibility = self.model.solve()

    def get_demand(self):
        return [d for d in demand(self.orders, self.days).values()]

    def get_inventory(self):
        return peek(self.inventory)

    def get_production(self):
        return peek(self.production)

    def get_purchases(self):
        return peek(self.purchases)
    
    def result_dict(self):
        return dict(demand=self.get_demand(),
                    prod=self.get_production(),
                    pur=self.get_purchases(),
                    inv=self.get_inventory())
    
    def dataframe(self):
        return pd.DataFrame(self.result_dict())

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    @property
    def obj_value(self):
        return pulp.value(self.model.objective)

TOTAL_DEMAND = 1500
N_DAYS = 7
sizer = Volume(100,150,1)
sim_volumes = generate_volumes(TOTAL_DEMAND, sizer)
pricer = Price(mean=150, delta=75)
orders = generate_orders(n_days=N_DAYS, total_volume=TOTAL_DEMAND, pricer=pricer, sizer=sizer)

m = Model("Single product", n_days=N_DAYS, max_capacity=500)
m.add_orders(orders)
m.set_objective()
m.set_non_zero_inventory()
m.set_closed_sum()
m.solve()

def almost_equals(a, b):
    return abs(a - b) < 0.1

assert almost_equals(sum(m.get_demand()), TOTAL_DEMAND)
inv, prod, pur = m.get_inventory(), m.get_production(), m.get_purchases()


df = m.dataframe()
print(df)
print()
print(df.sum())

os1 = [Order(day=0, volume=127.0, price=111.3),
 Order(day=0, volume=139.0, price=163.4),
 Order(day=0, volume=147.0, price=202.1),
 Order(day=3, volume=104.0, price=112.2),
 Order(day=2, volume=119.0, price=152.2),
 Order(day=3, volume=139.0, price=170.9),
 Order(day=0, volume=142.0, price=75.7),
 Order(day=5, volume=118.0, price=84.7),
 Order(day=0, volume=148.0, price=106.7),
 Order(day=6, volume=122.0, price=105.2),
 Order(day=0, volume=144.0, price=86.1),
 Order(day=2, volume=51.0, price=187.0)]