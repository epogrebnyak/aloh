import warnings
from dataclasses import dataclass
from enum import Enum
from random import choice, uniform
from typing import List, Dict

import pandas as pd
import numpy
import pulp


LpExpression = pulp.pulp.LpAffineExpression


warnings.simplefilter("ignore")


class Product(Enum):
    A = "H"
    B = "H10"
    C = "TA-HSA-10"
    D = "TA-240"


@dataclass
class Order:
    day: int
    volume: float
    price: float


OrderBatch = Dict[Product, List[Order]]
CapacityBatch = Dict[Product, float]


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
    round_to: float = 1.0

    def generate(self) -> float:
        x = uniform(self.min_order, self.max_order)
        return rounds(x, self.round_to)


def generate_volumes(total_volume: float, sizer: Volume) -> List[float]:
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


def generate_orders(n_days, total_volume, pricer, sizer):
    sim_volumes = generate_volumes(total_volume, sizer)
    n = len(sim_volumes)
    days = days_list(n_days)
    sim_days = [choice(days) for _ in range(n)]
    sim_prices = [pricer.generate() for _ in range(n)]
    return [Order(d, v, p) for (d, v, p) in zip(sim_days, sim_volumes, sim_prices)]


def demand(orders, days: list):
    dict_ = dict([(d, 0) for d in days])
    for order in orders:
        dict_[order.day] += order.volume
    return dict_


def demand_dataframe(orders, n_days: int):
    df = pd.DataFrame(0, columns=["volume"], index=days_list(n_days))
    for order in orders:
        df.loc[order.day, "volume"] += order.volume
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


# import numpy
# >>> a = numpy.zeros(shape=(5,2))


class Model:
    obj = pulp.LpMaximize

    def __init__(self, name="Planning model", n_days=1):
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))

    def add_production(self, max_capacity):
        self.production = pulp.LpVariable.dicts(
            "Production", self.days, lowBound=0, upBound=max_capacity
        )

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
            daily_orders_sum = [
                order.volume * accept[i]
                for i, order in enumerate(orders)
                if d == order.day
            ]
            purchases[d] = pulp.lpSum(daily_orders_sum)
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
        return dict(
            demand=self.get_demand(),
            sold=self.get_purchases(),
            prod=self.get_production(),
            inv=self.get_inventory(),
        )

    def dataframe(self):
        return pd.DataFrame(self.result_dict())

    def satisfied_demand(self):
        df = self.dataframe()
        return df.sum().sold / df.sum().demand

    def total_capacity(self):
        return sum([self.production[d].upBound for d in self.days])

    def load_factor(self):
        return self.dataframe().sum()["prod"] / self.total_capacity()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    @property
    def obj_value(self):
        return pulp.value(self.model.objective)


N_DAYS = 7
orders_a = generate_orders(
    n_days=N_DAYS,
    total_volume=1400,
    sizer=Volume(min_order=100, max_order=200, round_to=20),
    pricer=Price(mean=150, delta=30),
)

orders_b = generate_orders(
    n_days=N_DAYS,
    total_volume=700,
    sizer=Volume(min_order=80, max_order=120, round_to=5),
    pricer=Price(mean=50, delta=15),
)
orders = orders_a

order_batch = {Product.A: orders_a, Product.B: orders_b}
capacity_batch = {Product.A: 200, Product.B: 100}


TOTAL_DEMAND = 1400
m = Model("Single product", n_days=N_DAYS)
m.add_production(max_capacity=200)
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

os1 = [
    Order(day=0, volume=127.0, price=111.3),
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
    Order(day=2, volume=51.0, price=187.0),
]


class MultiProductModel:
    obj = pulp.LpMaximize

    def __init__(self, name="Several products model", n_days=7, all_products=Product):
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))
        self.all_products = all_products
        self.dims = len(all_products), n_days
        # нулевые производственные мощности
        self.production = {}
        self.set_daily_capacity({p: 0 for p in all_products})

    def set_daily_capacity(self, daily_capacity: CapacityBatch):
        for p, cap in daily_capacity.items():
            self.production[p] = pulp.LpVariable.dict(
                f"Production_{p.name}", self.days, lowBound=0, upBound=cap
            )

    def add_orders(self, order_batch: OrderBatch):
        self.order_batch = order_batch
        self.accept_batch = dict()
        for p, orders in order_batch.items():
            order_nums = range(len(orders))
            self.accept_batch[p] = pulp.LpVariable.dicts(
                f"{p.name}_AcceptOrder", order_nums, cat="Binary"
            )
        self.create_purchases()
        return self.accept_batch

    def create_empty_expression_dict(self):
        return {p: [pulp.lpSum(0) for d in self.days] for p in self.all_products}

    def create_purchases(self):
        """Purchases are accepted orders."""
        self.purchases = self.create_empty_expression_dict()
        for p, orders in self.order_batch.items():
            accept = self.accept_batch[p]
            for d in self.days:
                daily_orders_sum = [
                    order.volume * accept[i]
                    for i, order in enumerate(orders)
                    if d == order.day
                ]
                self.purchases[p][d] = pulp.lpSum(daily_orders_sum)
        return self.purchases

    def sales_expression(self):
        expr_list = []
        for p, orders in self.order_batch.items():
            accept = self.accept_batch[p]
            a = [
                order.volume * order.price * accept[i] for i, order in enumerate(orders)
            ]
            expr_list.extend(a)
        return expr_list

    def set_objective(self):
        self.model += pulp.lpSum(self.sales_expression())

    def set_non_zero_inventory(self):
        self.inventory = self.create_empty_expression_dict()
        for p in self.all_products:
            prod = self.production[p]
            pur = self.purchases[p]
            for d in self.days:
                self.inventory[p][d] = accumulate(prod, d) - accumulate(pur, d)
                self.model += (
                    self.inventory[p][d] >= 0,
                    f"Positive inventory of {p} at day {d}",
                )

    def solve(self):
        self.feasibility = self.model.solve()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    @property
    def obj_value(self):
        return pulp.value(self.model.objective)

    def set_closed_sum(self):
        for p in self.all_products:
            self.model += pulp.lpSum(self.production[p]) == pulp.lpSum(
                self.purchases[p]
            )


def evaluate(holder):
    return {p: [item.value() for item in holder[p]] for p in holder.keys()}


def evaluate_dict(holder):
    return {p: [item.value() for item in holder[p].values()] for p in holder.keys()}


N_DAYS = 7
orders_a = generate_orders(
    n_days=N_DAYS,
    total_volume=1400,
    sizer=Volume(min_order=100, max_order=300, round_to=20),
    pricer=Price(mean=150, delta=30),
)

orders_b = generate_orders(
    n_days=N_DAYS,
    total_volume=300,
    sizer=Volume(min_order=80, max_order=120, round_to=5),
    pricer=Price(mean=50, delta=15),
)
order_batch = {Product.A: orders_a, Product.B: orders_b}
capacity_batch = {Product.A: 200, Product.B: 100}


mp = MultiProductModel(n_days=7, all_products=Product)
mp.set_daily_capacity({Product.A: 200, Product.B: 100})
mp.add_orders(order_batch)
mp.set_non_zero_inventory()
mp.set_closed_sum()
mp.set_objective()
mp.solve()
prod = evaluate_dict(mp.production)
pur = evaluate(mp.purchases)
inv = evaluate(mp.inventory)
accept = evaluate_dict(mp.accept_batch)


def df(d):
    return pd.DataFrame(d)


# TODO:
# demand_dataframe(order_batch[Product.A], 7)

print("\nПроизводство")
print(df(prod))
print("\nПокупки")
print(df(pur))
print("\nЗапасы")
print(df(inv))

# Тесты

assert mp.production[Product.A][0].name == "Production_A_0"
assert mp.production[Product.A][0].upBound == 200
assert mp.production[Product.B][6].upBound == 100
se = mp.sales_expression()
assert len(accept[Product.A]) == len(orders_a)
assert len(accept[Product.B]) == len(orders_b)


assert sum(prod[Product.A]) == sum(pur[Product.A])
assert sum(prod[Product.B]) == sum(pur[Product.B])
