import pulp

from collections import UserDict
from dataclasses import dataclass


class ProductDict(UserDict):
    pass

    def pick(self, key):
        return {k: v[key] for k, v in self.items()}

    def max_day(self):
        return max([order.day for k in self.keys() for order in self[k]["orders"]])

    def days(self):
        return list(range(self.max_day() + 1))

    def products(self):
        return list(self.keys())


def accum(var, i):
    return pulp.lpSum([var[k] for k in range(i + 1)])


def multiply(vec, mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = vec[p] * mat[p][d]
    return res


def lp_sum(mat):
    return pulp.lpSum([mat[p][d] for p in mat.keys() for d in mat[p].keys()])


def values(mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = pulp.value(mat[p][d])
    return res


@dataclass
class Order:
    """Параметры заказа."""

    day: int
    volume: float
    price: float


def make_accept_dict(order_dict):
    accept = {}
    for p in order_dict.keys():
        accept[p] = [
            pulp.LpVariable(f"Accept_{p}_{i}", cat="Binary")
            for i, order in enumerate(order_dict[p])
        ]
    return accept


@dataclass
class Dim:
    products: [str]
    days: list

    def empty_matrix(self):
        return {p: {d: 0 for d in self.days} for p in self.products}

    def make_production(self, capacities):
        prod = self.empty_matrix()
        for p in self.products:
            cap = capacities[p]
            for d in self.days:
                prod[p][d] = pulp.LpVariable(f"Prod_{p}_{d}", lowBound=0, upBound=cap)
        return prod

    def make_shipment_sales(self, order_dict, accept_dict):
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

    def calculate_inventory(self, prod, ship):
        inv = self.empty_matrix()
        for p in self.products:
            xs = prod[p]
            ys = ship[p]
            for d in self.days:
                inv[p][d] = accum(xs, d) - accum(ys, d)
        return inv


class OptModel:
    def __init__(self, product_dict: ProductDict, **kwargs):
        name = kwargs["model_name"]

        self.order_dict = product_dict.pick("orders")
        self.accept_dict = make_accept_dict(self.order_dict)

        capacities = product_dict.pick("capacity")
        unit_costs = product_dict.pick("unit_cost")

        self.products = product_dict.products()
        self.days = product_dict.days()
        dim = Dim(self.products, self.days)

        self.prod = dim.make_production(capacities)
        self.costs = multiply(unit_costs, self.prod)
        self.ship, self.sales = dim.make_shipment_sales(
            self.order_dict, self.accept_dict
        )
        self.inv = dim.calculate_inventory(self.prod, self.ship)
        self.model = pulp.LpProblem(name, pulp.LpMaximize)

    def set_objective(self):
        # Целевая функция
        self.model += lp_sum(self.sales) - lp_sum(self.costs)

    def set_non_negative_inventory(self):
        # Ограничение 1: неотрицательные запасы
        for p in self.products:
            for d in self.days:
                self.model += (self.inv[p][d] >= 0, f"Non_negative_inventory_{p}_{d}")

    def set_closed_sum(self):
        # Ограничение 2: закрытая сумма
        for p in self.products:
            self.model += (
                pulp.lpSum(self.prod[p]) == pulp.lpSum(self.ship[p]),
                f"Closed sum for {p}",
            )

    def evaluate(self):
        self.set_objective()
        self.set_non_negative_inventory()
        self.set_closed_sum()
        self.model.solve()

    def accept_orders(self):
        return {p: [int(x.value()) for x in self.accept_dict[p]] for p in self.products}


import pandas as pd


def series(var, p):
    return values(var)[p].values()


def product_dataframe(p, prod, ship, inv, sales, costs):
    df = pd.DataFrame()
    df["x"] = series(prod, p)
    df["ship"] = series(ship, p)
    df["inv"] = series(inv, p)
    df["sales"] = series(sales, p)
    df["costs"] = series(costs, p)
    return df


def product_dataframes(m):
    dfs = {}
    for p in m.products:
        dfs[p] = product_dataframe(p, m.prod, m.ship, m.inv, m.sales, m.costs)
    return dfs


def as_df(mat):
    return pd.DataFrame(values(mat))

def variable_dataframes(m):
    return map(as_df, [m.prod, m.ship, m.inv, m.sales, m.costs])

