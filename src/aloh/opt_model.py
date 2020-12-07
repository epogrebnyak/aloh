"""Выбор заказов и расчетов объемов производства по нескольким продуктам."""
import warnings
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd  # type: ignore
import pulp  # type: ignore

from orderbook import (
    Order,
    empty_matrix,
    get_sales,
    get_shipment,
    make_accept_variables,
)
from production import Machine, ProductName, prod_and_cost

warnings.simplefilter("ignore")


def accumulate(var, i):
    return pulp.lpSum([var[k] for k in range(i + 1)])


@dataclass
class OptModel:
    name: str
    n_days: int
    products: List[ProductName]
    order_dict: Dict[ProductName, List[Order]]
    plant: Dict[ProductName, Machine]
    storage_days: Dict[ProductName, int]
    # TODO: small penalty size should not affect the modelling result
    inventory_penalty: float = 0.1
    objective_type: int = pulp.LpMaximize
    feasibility: int = 0

    def __post_init__(self):
        self.prod, self.costs = prod_and_cost(self.plant, self.n_days)
        self.accept_dict = make_accept_variables(self.order_dict)
        self.ship = get_shipment(self.n_days, self.order_dict, self.accept_dict)
        self.sales = get_sales(self.n_days, self.order_dict, self.accept_dict)
        self.model = pulp.LpProblem(self.name, self.objective_type)
        # TODO: requirement should include full capacity
        self.req = self.ship

    def set_storage_limit(self):
        """Ввести ограничение на срок складирования продукта."""
        for p in self.products:
            s = self.storage_days[p]
            for d in range(self.n_days):
                self.model += accumulate(self.prod[p], d) <= accumulate(
                    self.req[p], min(self.n_days, d + s)
                )

    def set_non_negative_inventory(self):
        """Установить неотрицательную величину запасов.
        Без этого требования запасы переносятся обратно во времени.
        """
        self.inventory = empty_matrix(self.n_days, self.products, pulp.lpSum(0))
        for p in self.products:
            prod = self.prod[p]
            req = self.req[p]
            for d in range(self.n_days):
                self.inventory[p][d] = accumulate(prod, d) - accumulate(req, d)
                self.model += (
                    self.inventory[p][d] >= 0,
                    f"Non-negative inventory of {p} at day {d}",
                )

    def set_closed_sum(self):
        """Установить производство равным объему покупок."""
        for p in self.products:
            self.model += pulp.lpSum(self.prod[p]) == pulp.lpSum(self.req[p])

    def inventory_items(self):
        """Штраф за хранение запасов, для целевой функции."""
        # TODO: установить в % от цены продукта, аналог production.sales()
        m = self.inventory_penalty
        xs = [
            m * self.inventory[p][d] for p in self.products for d in range(self.n_days)
        ]
        return pulp.lpSum(xs)

    def set_objective(self):
        self.model += (
            pulp.lpSum(self.sales) - pulp.lpSum(self.costs) - self.inventory_items()
        )

    def solve(self):
        self.feasibility = self.model.solve()

    def evaluate(self):
        self.set_non_negative_inventory()
        self.set_closed_sum()
        self.set_storage_limit()
        self.set_objective()
        self.solve()
        return (
            evaluate_vars(self.accept_dict),
            evaluate_vars(self.prod),
        )

    def save(self, filename: str = ""):
        fn = filename if filename else self.default_filename
        self.model.writeLP(fn)
        print(f"Cохранили модель в файл {fn}")

    @property
    def default_filename(self):
        return self.name.lower().replace(" ", "_").replace(".", "_") + ".lp"


def evaluate_expr(holder):
    """Получить словарь со значениями выражений"""
    return {p: [my_round(item.value()) for item in holder[p]] for p in holder.keys()}


def evaluate_vars(holder):
    """Получить словарь со значениями переменных"""
    return {
        p: [my_round(item.value()) for item in holder[p].values()]
        for p in holder.keys()
    }


def my_round(x):
    if x is None:
        return None
    else:
        return round(x, 1)


# Функции для просмотра результатов


def collect(orders: List[Order], days: List):
    acc = [0 for _ in days]
    for order in orders:
        acc[order.day] += order.volume
    return acc


def demand_dict(m: OptModel):
    return {p: collect(m.order_book[p], range(m.n_days)) for p in m.order_book.products}


def df(dict_, index_name="день"):
    df = pd.DataFrame(dict_)
    df.index.name = index_name
    return df


def order_status(m: OptModel, p: ProductName):
    res = []
    for order, status in zip(m.order_book[p], m.order_book.accept_dict[p].values()):
        x = order.__dict__
        x["accepted"] = True if status.value() == 1 else False
        res.append(x)
    return sorted(res, key=lambda x: x["day"])


def order_status_all(m):
    return {p: order_status(m, p) for p in m.order_book.products}


def obj_value(m):
    return pulp.value(m.model.objective)


def daily_capacity(m):
    return {p: [cap for _ in range(m.n_days)] for p, cap in m.plant.capacity.items()}


def get_values(m):
    return dict(
        all_products=m.products,
        demand=demand_dict(m),
        order_status=order_status_all(m),
        capacity=m.plant.capacity,
        capacity_list=daily_capacity(m),
        prod=evaluate_vars(m.plant.production),
        ship=evaluate_expr(m.order_book.shipment),
        req=evaluate_expr(m.requirement),
        inv=evaluate_expr(m.inventory),
        n_days=m.n_days,
        sales=m.order_book.sales.value(),
        costs=m.plant.costs.value(),
        obj=obj_value(m),
        status=m.feasibility,
    )


def summary_df(v):
    prop = df(
        {
            "capacity": df(v["capacity_list"]).sum(),
            "orders": df(v["demand"]).sum(),
            "purchase": df(v["ship"]).sum(),
            "internal_use": df(v["req"]).sum() - df(v["ship"]).sum(),
            "requirement": df(v["req"]).sum(),
            "production": df(v["prod"]).sum(),
            "avg_inventory": df(v["inv"]).mean().round(1),
        },
        "",
    )
    return prop.T


def print_solution(m):
    v = get_values(m)

    print("\nСтатус решения:", v["status"])

    print("\nПериод планирования, дней:", v["n_days"])

    print("\nМощности производства, тонн в день:")
    for p, cap in v["capacity"].items():
        print(" ", p, cap)

    for p in v["all_products"]:
        print("\nЗаказы на продукт", p)
        order_df = df(v["order_status"][p], "N заказа")
        print(order_df)

    print("\nСпрос (тонн)")
    print(df(v["demand"]))

    print("\nОтгрузка (тонн)")
    print(df(v["ship"]))

    print("\nПроизводство (тонн)")
    print(df(v["prod"]))

    print("\nЗапасы (тонн)")
    print(df(v["inv"]))

    print("\nОбъемы мощностей, заказов, производства, покупок (тонн)")
    print(summary_df(v))

    print("\nВыручка (долл.США):  %0.0f" % v["sales"])
    print("Затраты (долл.США):  %0.0f" % v["costs"])
    print("Прибыль (долл.США):  %0.0f" % (v["sales"] - v["costs"]))

    print("\nЦелевая функция:     %0.0f" % v["obj"])
    print_solvers()


def lst(xs):
    return ", ".join(xs)


def print_solvers():
    """
    Информация по солверам.

    Дополнительные ссылки:
    - https://github.com/coin-or/Cbc
    - https://en.wikipedia.org/wiki/Branch_and_cut
    - https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html
    """
    print("\nВозможные солверы:", lst(pulp.list_solvers()))
    print("Доступные:  ", lst(pulp.list_solvers(onlyAvailable=True)))
    default_solver = pulp.LpSolverDefault  # 'PULP_CBC_CMD'
    print("Использован:", default_solver.name)
    print("Где находится:", pulp.get_solver(default_solver.name).path)


def useful_stats(m):
    values = get_values(m)
    return dict(
        values=values,
        df=summary_df(values),
        order_dict=values["order_status"],
        prod=values["prod"],
    )
