"""Выбор заказов и расчетов объемов производства по нескольким продуктам.

Особенности реализации 
----------------------

- введен класса Product (перечислимый тип Enum с обозначением продуктов),
  он используется ключ словарей с данными по продуктам
- в PuLP задача проще формулируется по строкам, чем в матрице, в модели 
  оптимизации данные организованы как словари по продуктам (характерно для PuLP)

Known issues
------------

- может понадобиться команда set PYTHONIOENCODING=utf8  
- pulp не очень хорошо транслирует типы для mypy
- можно поменять print на логирование

"""
import warnings
from dataclasses import dataclass, field
from enum import Enum
from random import choice, uniform
from typing import Dict, List

import pandas as pd  # type: ignore
import pulp  # type: ignore
import numpy as np  # type: ignore


warnings.simplefilter("ignore")


class Product(Enum):
    """Виды продуктов.

    Использование:

    >>> [p for in Product] # перечисление
    >>> Product.A          # обозначение продукта
    >>> Product.A.name
    """

    A = "H"
    B = "H10"
    C = "TA-HSA-10"
    D = "TA-240"


def empty_matrix(n_days, products):
    return {p: [pulp.lpSum(0) for d in range(n_days)] for p in products}


# Имитация портфеля заказов


@dataclass
class Order:
    """Параметры заказа."""

    day: int
    volume: float
    price: float


OrderDict = Dict[Product, List[Order]]
ProductParamDict = Dict[Product, float]
# FIXME: дает ошибку типа в проверке mypy
LpExpression = pulp.pulp.LpAffineExpression


def rounds(x, step=1):
    """Округление, обычно до 5 или 10. Используется для выравнивания объема заказа."""
    return round(x / step, 0) * step


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
        if remaining == 0:
            xs.append(x)
            break
        elif remaining > 0:
            xs.append(x)
        else:
            # добавить небольшой остаток, котрый ведет
            # сумму *хs* на величину *total_volume*
            xs.append(total_volume - sum(xs))
            break
    return xs


def generate_day(n_days: int) -> int:
    return choice(range(n_days))


def generate_orders(n_days: int, total_volume: float, pricer: Price, sizer: Volume):
    """Создать гипотетический список заказов."""
    days = list(range(n_days))
    sim_volumes = generate_volumes(total_volume, sizer)
    n = len(sim_volumes)
    sim_days = [choice(days) for _ in range(n)]
    sim_prices = [pricer.generate() for _ in range(n)]
    return [Order(d, v, p) for (d, v, p) in zip(sim_days, sim_volumes, sim_prices)]


@dataclass
class Machine:
    """Параметры производства одного продукта:

    - максимальный выпуск в день (мощность)
    - переменная стоимость производства, долл/т
    - максимальный срок хранения продукта на складе, дней
    - прямое потребление других продуктов, необходимое для выпуск 1 т данного продукта
    """

    product: Product
    capacity: float
    unit_cost: float
    storage_days: int
    requires: ProductParamDict = field(default_factory=dict)


def production(capacity_dict, n_days):
    """Создать переменные объема производства, ограничить снизу нулем
        и сверху мощностью."""
    days = list(range(n_days))
    production = {}
    for p, cap in capacity_dict.items():
        production[p] = pulp.LpVariable.dict(
            f"Production_{p.name}", days, lowBound=0, upBound=cap
        )
    return production


def product_dataframe(arr, products=Product):
    return pd.DataFrame(arr, columns=products, index=products)


def full_requirement_multipliers(p: Product, R) -> dict:
    row = np.array([(1 if x == p else 0) for x in Product])
    vec = np.matmul(row, R.to_numpy())
    return {p: m for m, p in zip(vec, Product) if m}


@dataclass
class Plant:
    """Завод состоит из нескольких производств (Unit)."""

    units: List[Machine]
    n_days: int = 0

    def __post_init__(self):
        assert len(set(self.products)) == len(self.units)
        self.production = production(self.capacity, self.n_days)

    @property
    def products(self):
        return [u.product for u in self.units]

    @property
    def capacity(self):
        return {u.product: u.capacity for u in self.units}

    @property
    def storage_days(self):
        return {u.product: u.storage_days for u in self.units}

    @property
    def unit_costs(self):
        return {u.product: u.unit_cost for u in self.units}

    def direct_material_requirement(self, echo=False):
        """
        B - матрица прямых затрат
        """
        B = product_dataframe(arr=0)
        for u in self.units:
            p = u.product
            for k, v in u.requires.items():
                if echo:
                    print("На 1 тонну", p.name, "используется", v, "тонн", k.name)
                B.loc[p, k] = v
        return B

    def full_material_requirement(self):
        """
        R - матрица полных затрат
        """
        B = self.direct_material_requirement()
        n = B.shape[0]
        return product_dataframe(np.linalg.inv(np.identity(n) - B))

    def costs(self) -> LpExpression:
        """Элементы расчета величины затрат на производство в деньгах."""
        xs = []
        for p in self.products:
            prod = self.production[p]
            for x in prod.values():
                xs.append(x * self.unit_costs[p])
        return pulp.lpSum(xs)


# Оптимизационная модель


def accept_dict(order_dict):
    """Cоздать бинарные переменные (принят/не принят заказ).
           вида <P>_AcceptOrder_<k>
    """
    accept_dict = {p: dict() for p in order_dict.keys()}
    for p, orders in order_dict.items():
        order_nums = range(len(orders))
        accept_dict[p] = pulp.LpVariable.dicts(
            f"{p.name}_AcceptOrder", order_nums, cat="Binary"
        )
    return accept_dict


def purchases(mat, order_dict, accept_dict):
    for p, orders in order_dict.items():
        accept = accept_dict[p]
        for d, _ in enumerate(mat[p]):
            daily_orders_sum = [
                order.volume * accept[i]
                for i, order in enumerate(orders)
                if d == order.day
            ]
            mat[p][d] = pulp.lpSum(daily_orders_sum)
    return mat


@dataclass
class OrderBook:
    order_dict: OrderDict
    n_days: int = 0

    @property
    def products(self):
        return [x for x in self.order_dict.keys()]

    def __post_init__(self):
        self.accept_dict = accept_dict(self.order_dict)
        mat = empty_matrix(self.n_days, self.products)
        self.purchases = purchases(mat, self.order_dict, self.accept_dict)

    def sales(self):
        return pulp.lpSum(
            order.volume * order.price * self.accept_dict[p][i]
            for p, orders in self.order_dict.items()
            for i, order in enumerate(orders)
        )


def total_requirement(plant: Plant, order_book: OrderBook):
    requirement = empty_matrix(order_book.n_days, order_book.products)
    R = plant.full_material_requirement()
    for p1 in plant.products:
        # для продукта p1 мы знаем потребности в остальных продуктах
        full_req = full_requirement_multipliers(p1, R)
        for d in range(order_book.n_days):
            wanted = order_book.purchases[p1][d]
            # итерируем по компонентам продукта p1
            for p2, m in full_req.items():
                requirement[p2][d] += wanted * m
    return requirement


def accumulate(var, i) -> LpExpression:
    return pulp.lpSum([var[k] for k in range(i + 1)])


@dataclass
class OptModel:
    name: str
    n_days: int
    order_book: OrderBook
    plant: Plant
    inventory_penalty: float = 0.1
    objective_type: int = pulp.LpMaximize

    def __post_init__(self):
        # одинаковая размерность
        assert self.order_book.products == self.plant.products
        self.products = self.plant.products
        self.order_book = OrderBook(self.order_book.order_dict, self.n_days)
        self.plant = Plant(self.plant.units, self.n_days)
        # модель
        self.model = pulp.LpProblem(self.name, self.objective_type)
        self.requirement = total_requirement(self.plant, self.order_book)

    def set_storage_limit(self):
        """Ввести ограничение на срок складирования продукта."""
        for p in self.plant.products:
            s = self.plant.storage_days[p]
            for d in range(self.n_days):
                try:
                    self.model += accumulate(self.plant.production[p], d) <= accumulate(
                        self.requirement[p], d + s
                    )
                except IndexError:
                    # Мы не распространяем условие на последние s дней периода
                    pass

    def set_non_negative_inventory(self):
        """Установить неотрицательную величину запасов.
        Без этого требования запасы переносятся обратно во времени.
        """
        self.inventory = empty_matrix(self.n_days, self.products)
        for p in self.products:
            prod = self.plant.production[p]
            req = self.requirement[p]
            for d in range(self.n_days):
                self.inventory[p][d] = accumulate(prod, d) - accumulate(req, d)
                self.model += (
                    self.inventory[p][d] >= 0,
                    f"Non-negative inventory of {p.name} at day {d}",
                )

    def set_closed_sum(self):
        """Установить производство равным объему покупок."""
        for p in self.products:
            self.model += pulp.lpSum(self.plant.production[p]) == pulp.lpSum(
                self.requirement[p]
            )

    def inventory_items(self):
        """Штраф за хранение запасов, для целевой функции."""
        m = self.inventory_penalty
        xs = [
            m * self.inventory[p][d] for p in self.products for d in range(self.n_days)
        ]
        return pulp.lpSum(xs)

    def set_objective(self):
        self.model += (
            self.order_book.sales() - self.plant.costs() - self.inventory_items()
        )

    def solve(self):
        self.feasibility = self.model.solve()

    def evaluate(self):
        self.set_non_negative_inventory()
        self.set_storage_limit()
        self.set_closed_sum()
        self.set_objective()
        self.solve()
        return (
            evaluate_vars(self.order_book.accept_dict),
            evaluate_vars(self.plant.production),
        )

    def save(self, filename: str = ""):
        fn = filename if filename else self.name.lower().replace(" ", "_") + ".lp"
        self.model.writeLP(fn)
        print(f"Мы сохранили модель в файл {fn}")


# Функции для просмотра результатов


def collect(orders: List[Order], days: List):
    acc = [0 for _ in days]
    for order in orders:
        acc[order.day] += order.volume
    return acc


def demand_dict(m: OptModel):
    return {
        p: collect(orders, range(m.n_days))
        for p, orders in m.order_book.order_dict.items()
    }


def evaluate_expr(holder):
    """Получить словарь со значениями выражений"""
    return {p: [round(item.value(), 1) for item in holder[p]] for p in holder.keys()}


def evaluate_vars(holder):
    """Получить словарь со значениями переменных"""
    return {
        p: [round(item.value(), 1) for item in holder[p].values()]
        for p in holder.keys()
    }


def df(dict_, index_name="день"):
    df = pd.DataFrame(dict_)
    df.index.name = index_name
    return df


def order_status(m, p: Product):
    res = []
    for order, status in zip(
        m.order_book.order_dict[p], m.order_book.accept_dict[p].values()
    ):
        x = order.__dict__
        x["accepted"] = True if status.value() == 1 else False
        res.append(x)
    return sorted(res, key=lambda x: x["day"])


def order_status_all(m):
    return {p: order_status(m, p) for p in m.order_book.order_dict.keys()}


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
        ship=evaluate_expr(m.order_book.purchases),
        req=evaluate_expr(m.requirement),
        inv=evaluate_expr(m.inventory),
        n_days=m.n_days,
        sales=m.order_book.sales().value(),
        costs=m.plant.costs().value(),
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
        print(f"  {p.name}:", cap)

    for p in v["all_products"]:
        print("\nЗаказы на продукт", p.name)
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
