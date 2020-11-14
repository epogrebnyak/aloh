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


@dataclass
class Order:
    product: str
    day: int
    volume: float
    price: float


def generate_between(a, b):
    return uniform(a, b)


def generate_day(n_days: int) -> int:
    return choice(range(n_days))


def rounds(x, f=1):
    """Округление, обычно до 5 или 10."""
    return round(x / f, 0) * f


@dataclass
class Volume:
    min_order: float
    max_order: float
    rounding_factor: float = 1.0

    def generate_one(self) -> float:
        x = generate_between(self.min_order, self.max_order)
        return rounds(x, self.rounding_factor)
    
    def generate_many(self, total_volume: float)-> List[float]:
        xs = []
        remaining = total_volume
        while remaining >= 0:
            x = self.generate_one()
            remaining = remaining - x
            if remaining >= 0:
                xs.append(x)
            else:
                xs.append(total_volume - sum(xs))
        return xs    




@dataclass
class Price:
    mean: float
    delta: float

    def generate(self):
        p = uniform(self.mean - self.delta, self.mean + self.delta)
        return round(p, 1)


def yield_orders(n_days, product, total_volume, sizer:Volume, pricer:Price):
    for volume in sizer.generate_many(total_volume):
        day = generate_day(n_days)
        price = pricer.generate()
        yield Order(product.name, day, volume, price)


@dataclass
class OrderGenerator:
    product: Product
    sizer: Volume
    pricer: Price
    
    def generate_orders(self, n_days, total_volume):
        gen = yield_orders(n_days, self.product, total_volume, self.sizer, self.pricer)
        return list(gen)




def sorted_list(orders):
    return sorted(orders, key=lambda o: o.day)


def days_list(n_days: int):
    return list(range(n_days))


def zero_df(n_days):
    return pd.DataFrame(0, columns=[p.name for p in Product], index=days_list(n_days))


def dataframe(orders):
    return pd.DataFrame([s.__dict__ for s in sorted_list(orders)])


def dataframe_accepted(orders, accept):
    df = dataframe(orders)
    df["accept"] = int(0)
    for i in accept.keys():
        df.loc[i, "accept"] = int(accept[i].value())
    return df.sort_values(["day", "price"])


def demand_dataframe(orders, n_days):
    df = zero_df(n_days)
    for order in orders:
        df.loc[order.day, order.product] += order.volume
    df.index.name = "day"
    return df


def dataframe_final(n_days, product_name, orders, production, purchases, inventory):
    product_name = "A"
    final = demand_dataframe(orders, n_days)[[product_name]].rename(
        columns={product_name: "Demand"}
    )
    final["Purchases"] = purchases
    final["Production"] = production
    final["Inventory"] = inventory
    return final



def make_purchases(orders, days, accept):
    """Purchases are accepted orders."""
    purchases = dict()
    for d in days:
        daily_orders = [
            order.volume * accept[i] for i, order in enumerate(orders) if d == order.day
        ]
        purchases[d] = pulp.lpSum(daily_orders)
    return purchases


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
        self.purchases = make_purchases(orders, self.days, self.accept)

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

    def get_inventory(self):
        return peek(self.inventory)

    def get_production(self):
        return peek(self.production)

    def get_purchases(self):
        return peek(self.purchases)

    def status(self):
        return pulp.LpStatus[self.feasibility]

    @property
    def obj_value(self):
        return pulp.value(self.model.objective)

TOTAL_DEMAND = 3500
gen = OrderGenerator(product=Product.A,
             sizer=Volume(min_order=300, max_order=700, rounding_factor=10),
             pricer=Price(mean=150, delta=75))
orders = gen.generate_orders(n_days=7, total_volume=TOTAL_DEMAND)
m = Model("Single product", n_days=7, max_capacity=500)

m.add_orders(orders)
m.set_objective()
m.set_non_zero_inventory()
feasibility = m.solve()


# print results

inv, prod, pur = m.get_inventory(), m.get_production(), m.get_purchases()
print(m.status())

total_prod = sum(m.get_production())

df = demand_dataframe(orders, 7)
assert df.A.sum() == 3500

print("Total production is", int(total_prod), "out of", TOTAL_DEMAND)

print("Load factor is %i%%" % (total_prod / TOTAL_DEMAND * 100))
print("Sales (objective) = %.1f thousand USD" % (m.obj_value / 10 ** 3))


# FIXME:
#print("ORDERS")
#print(demand_dataframe(orders, m.accept))

#print("DEMAND")
#print(dataframe_accepted(orders, m.accept))


final_df = dataframe_final(
    7, "A", orders, production=prod, purchases=pur, inventory=inv
)
print("\nProduct A")
print(final_df)
