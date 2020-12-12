from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List

import pandas as pd
import pulp

from .interface import Product, make_dataset

# This is a  dict of dicts that mimics a matrix.
# We need this data structure to work with pulp
Matrix = Dict[str, Dict[int, float]]

# Matrix manipulation and helpers


def multiply(vec: Dict, mat: Matrix):
    """Vector by matrix multiplication, results in a matrix."""
    res = {}
    for p in mat.keys():
        res[p] = {}
        m = vec[p]
        for d in mat[p].keys():
            res[p][d] = m * mat[p][d]
    return res


def lp_sum(mat: Matrix):
    return pulp.lpSum([mat[p][d] for p in mat.keys() for d in mat[p].keys()])


def values(mat: Matrix):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = pulp.value(mat[p][d])
    return res


def values_to_list(mat: Matrix):
    res = {}
    for p in mat.keys():
        res[p] = [pulp.value(x) for x in mat[p].values()]
    return res


# Orders


def make_accept_dict(order_dict):
    """Create a binary decision variable for each order."""
    accept = {}
    for p in order_dict.keys():
        accept[p] = [
            pulp.LpVariable(f"Accept_{p}_{i}", cat="Binary")
            for i, order in enumerate(order_dict[p])
        ]
    return accept


# Methods to work with (product * days) matrices


@dataclass
class Dim:
    """Hold product * days dimensions for matrices.
    Keeps fucntions that use these dimnsions together."""

    products: [str]
    days: list

    def empty_matrix(self):
        return {p: {d: 0 for d in self.days} for p in self.products}

    def make_production(self, capacities):
        """Create a decision variable for production:
        0 < prod[p][d] <  capacity[p],
        where p is product and d is day.
        """
        prod = self.empty_matrix()
        for p in self.products:
            cap = capacities[p]
            for d in self.days:
                prod[p][d] = pulp.LpVariable(f"Prod_{p}_{d}", lowBound=0, upBound=cap)
        return prod

    def make_shipment_sales(self, order_dict, accept_dict):
        """Create expressions for shipment (volume of daily off-take)
        and sales (same in dollars).
        """
        ship = self.empty_matrix()
        sales = self.empty_matrix()
        for p in self.products:
            for i, order in enumerate(order_dict[p]):
                for d in self.days:
                    if order.day == d:
                        a = accept_dict[p][i]
                        ship[p][d] += a * order.volume
                        sales[p][d] += a * order.volume * order.price
        return ship, sales

    def calculate_inventory(self, prod, use):
        """Create expressions for inventory.
        Inventory is end of day stock of produced, but not shipped goods.
        """
        inv = self.empty_matrix()
        for p in self.products:
            xs = prod[p]
            ys = use[p]
            for d in self.days:
                inv[p][d] = accum(xs, d) - accum(ys, d)
        return inv


def accum(var, i):
    return pulp.lpSum([var[k] for k in range(i + 1)])


class OptModel:
    def __init__(
        self, products: List[Product], model_name: str, inventory_weight: float
    ):
        dataset = make_dataset(products)

        self.order_dict = dataset.order_dict
        self.accept_dict = make_accept_dict(self.order_dict)

        self.capacities = dataset.capacities
        self.unit_costs = dataset.unit_costs
        self.storage_days = dataset.storage_days

        self.products = dataset.product_names
        self.days = dataset.days
        dim = Dim(self.products, self.days)

        self.prod = dim.make_production(self.capacities)
        self.costs = multiply(self.unit_costs, self.prod)
        self.ship, self.sales = dim.make_shipment_sales(
            self.order_dict, self.accept_dict
        )
        self.inv = dim.calculate_inventory(self.prod, self.ship)
        self.model = pulp.LpProblem(model_name, pulp.LpMaximize)
        self.inventory_weight = inventory_weight
        self.time_elapsed = 0

    def set_objective(self):
        # Целевая функция
        self.model += (
            lp_sum(self.sales)
            - lp_sum(self.costs)
            - lp_sum(self.inv) * self.inventory_weight
        )

    def set_non_negative_inventory(self):
        # Ограничение: неотрицательные запасы
        for p in self.products:
            for d in self.days:
                self.model += (self.inv[p][d] >= 0, f"Non_negative_inventory_{p}_{d}")

    def set_closed_sum(self):
        # Ограничение: закрытая сумма
        for p in self.products:
            self.model += (
                pulp.lpSum(self.prod[p]) == pulp.lpSum(self.ship[p]),
                f"Closed sum for {p}",
            )

    def set_storage_limit(self):
        """Ввести ограничение на срок складирования продукта."""
        for p in self.products:
            s = self.storage_days[p]
            for d in self.days:
                xs = next_use(self.ship[p], d, s)
                self.model += self.inv[p][d] <= pulp.lpSum(xs)

    def evaluate(self):
        self.set_objective()
        self.set_non_negative_inventory()
        self.set_closed_sum()
        self.set_storage_limit()
        self.solve()
        return self.accept_orders(), values_to_list(self.prod)

    def solve(self):
        start = perf_counter()
        self.model.solve()
        self.time_elapsed = perf_counter() - start
        print("Solved in {:.3f} sec".format(self.time_elapsed))

    def accept_orders(self):
        return {p: [int(x.value()) for x in self.accept_dict[p]] for p in self.products}

    def save(self, filename: str):
        self.model.writeLP(filename)
        print(f"Cохранили модель в файл {filename}")
        
    def orders_dataframe(self, p: str):
        return orders_dataframe(p, self)

    def product_dataframe(self, p: str):
        return product_dataframe(p, self)


def next_use(xs, d, s):
    """Slice *xs* list between *d* and *d+s* properly."""
    if s == 0:
        return 0
    else:
        last = len(xs) - 1
        up_to = min(last, d + s) + 1
        return [xs[t] for t in range(d + 1, up_to)]


# Data frame functions - report what is inside model


def orders_dataframe(p: str, m: OptModel):
    df = pd.DataFrame(m.order_dict[p])
    df["accept"] = m.accept_orders()[p]
    return df


def series(var, p: str):
    return values(var)[p].values()


def product_dataframe(p: str, m: OptModel):
    df = pd.DataFrame()
    df["x"] = series(m.prod, p)
    df["ship"] = series(m.ship, p)
    df["inv"] = series(m.inv, p)
    df["sales"] = series(m.sales, p)
    df["costs"] = series(m.costs, p)
    return df


def product_dataframes(m: OptModel):
    dfs = {}
    for p in m.products:
        dfs[p] = product_dataframe(p, m)
    return dfs


def as_df(mat):
    return pd.DataFrame(values(mat))


def variable_dataframes(m: OptModel):
    res = {}
    for key in ["prod", "ship", "inv", "sales", "costs"]:
        res[key] = as_df(m.__getattribute__(key))
    return res


# TODO:
"""Объемы мощностей, заказов, производства, покупок (тонн)
                    A       B
capacity       2800.0  1400.0
orders         3780.0  1120.0
purchase       2280.0   400.0
internal_use    500.0     0.0
requirement    2780.0   400.0
production     2780.0   400.0
avg_inventory   174.5     4.6"""
