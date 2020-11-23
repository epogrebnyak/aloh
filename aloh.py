"""Выбор заказов и расчетов объемов производства по нескольким продуктам.

Особенности реализации 
----------------------

- введен класса Product (перечислимый тип Enum с обозначением продуктов),
  он используется ключ словарей с данными по продуктам
- в PuLP задача проще формулируется по строкам, чем в матрице, в модели 
  оптимизации данные организованы как словари по продуктам (характерно для PuLP)
  
Запуск  
------

pip install requirements.txt  
set PYTHONIOENCODING=utf8  
python aloh.py > aloh.txt
cat aloh.txt
python example1.py > example1.txt
cat example1.txt
  
Known issues
------------

- может понадобиться команда set PYTHONIOENCODING=utf8  
- pulp не очень хорошо транслирует типы для mypy
- можно поменять print на логирование
- дублирование документации (README, этот докстринг, формулы в colab)

"""
import warnings
from dataclasses import dataclass, field
from enum import Enum
from random import choice, uniform
from typing import Dict, List, Generator, Union

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
DictOfExpressionLists = Dict[Product, List[LpExpression]]


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
class Unit:
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


@dataclass
class Plant:
    """Завод состоит из нескольких производств (Unit)."""

    units: List[Unit]

    def __post_init__(self):
        self.all_products = [u.product for u in self.units]
        self.assert_unique()

    def assert_unique(self):
        # гарантируем отсутствие дублирования параметров линий
        assert len(set(self.all_products)) == len(self.all_products)

    @property
    def storage_days(self):
        return {u.product: u.storage_days for u in self.units}

    @property
    def unit_costs(self):
        return {u.product: u.unit_cost for u in self.units}

    @property
    def capacity(self):
        return {u.product: u.capacity for u in self.units}

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


def product_dataframe(arr):
    return pd.DataFrame(arr, columns=Product, index=Product)


def full_requirement_multipliers(p: Product, R) -> dict:
    row = np.array([(1 if x == p else 0) for x in Product])
    vec = np.matmul(row, R.to_numpy())
    return {p: m for m, p in zip(vec, Product) if m}


# Оптимизационная модель


def accumulate(var, i) -> LpExpression:
    return pulp.lpSum([var[k] for k in range(i + 1)])


class PlantModel:
    """Оптимизационная модель звода.
    
    На входе:
    - количество дней периода планирования (n_days)
    - параметры производства (plant)
    - портфель заказов (order_dict)

    Используются ограничения (методы set_*):
    - неотрицательные остатки
    - сумма производства равна сумме потребления за период 
    
    Задается целевая функция (метод set_objective):    
    - выручка минус затраты минус штраф за хранение
    
    Определяются (decision variables):
        
    - <P>_AcceptOrder_<i> - бинарные переменые брать/не брать i-й заказ на продукт на продукт <P>
      метод .orders_accepted() или order_status_all()
      
    - Production_<P>_<d> - объем производства продукта <P> в день d
      метод .production_values()    

    Рассчитываются выражения (по дням и товарам):
    - inventories - остатки на складе на дням
    - purchases - отгрузка со склада по дням, тонн
    - internal_use - потребности внутреннего использования, тонн
    - requirement - общая потребность в товарах для отгрузки и для внутреннего использвоания, тонн
    
    В сумме за период:
    - sales - продажи, в денежном выражении
    - cost - затраты, в денежном выражении
    - штраф за хранение
    """

    obj = pulp.LpMaximize

    def __init__(self, name: str, n_days: int, plant: Plant, inventory_penalty=0.1):
        print("Название модели:", name)
        self.name = name
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))
        self.plant = plant
        self.inventory_penalty = inventory_penalty
        self._init_production()
        self.purchases = self._empty_matrix()
        self.internal_use = self._empty_matrix()
        self.requirement = self._empty_matrix()
        self.inventory = self._empty_matrix()

    def _empty_matrix(self):
        return {p: [pulp.lpSum(0) for d in self.days] for p in self.all_products}

    @property
    def all_products(self):
        return self.plant.all_products

    def daily_capacity(self):
        return {p: [cap for _ in self.days] for p, cap in self.plant.capacity.items()}

    def orders_accepted(self):
        return evaluate_vars(self.accept_dict)

    def production_values(self):
        return evaluate_vars(self.production)

    def _init_production(self):
        """Создать переменные объема производства, ограничить снизу нулем 
           и сверху мощностью."""
        self.production = {}
        for p, cap in self.plant.capacity.items():
            # создаем переменные вида Production_<P>_<d>
            self.production[p] = pulp.LpVariable.dict(
                f"Production_{p.name}", self.days, lowBound=0, upBound=cap
            )

    def add_orders(self, order_dict: OrderDict):
        """Добавить заказы и создать бинарные переменные (принят/не принят 
           заказ).
        """
        self.order_dict = order_dict
        self.accept_dict = {p: dict() for p in order_dict.keys()}
        for p, orders in order_dict.items():
            order_nums = range(len(orders))
            # создаем переменные вида <P>_AcceptOrder_<i>
            self.accept_dict[p] = pulp.LpVariable.dicts(
                f"{p.name}_AcceptOrder", order_nums, cat="Binary"
            )

        """Создать выражения для покупок каждого товара по дням."""
        for p, orders in order_dict.items():
            accept = self.accept_dict[p]
            for d in self.days:
                daily_orders_sum = [
                    order.volume * accept[i]
                    for i, order in enumerate(orders)
                    if d == order.day
                ]
                self.purchases[p][d] = pulp.lpSum(daily_orders_sum)

        """Создать выражения для совокупной потребности каждого товара."""
        R = self.plant.full_material_requirement()
        for p1 in self.all_products:
            # для продукта p1 мы знаем потребности в остальных продуктах
            full_req = full_requirement_multipliers(p1, R)
            for d in self.days:
                wanted = self.purchases[p1][d]
                for p2, m in full_req.items():
                    self.requirement[p2][d] += wanted * m

        """Создать выражения для внутреннего потребления товаров."""
        for p in self.all_products:
            for d in self.days:
                self.internal_use[p][d] = self.requirement[p][d] - self.purchases[p][d]

        """Ввести ограничение на срок складирования продукта."""
        for p in self.all_products:
            s = self.plant.storage_days[p]
            for d in self.days:
                try:
                    self.model += accumulate(self.production[p], d) <= accumulate(
                        self.requirement[p], d + s
                    )
                except IndexError:
                    # Мы не распространяем условие на последние s дней периода
                    pass

    def set_non_negative_inventory(self):
        """Установить неотрицательную величину запасов.
           Без этого требования запасы переносятся обратно во времени.
        """
        for p in self.all_products:
            prod = self.production[p]
            req = self.requirement[p]
            for d in self.days:
                self.inventory[p][d] = accumulate(prod, d) - accumulate(req, d)
                self.model += (
                    self.inventory[p][d] >= 0,
                    f"Non-negative inventory of {p.name} at day {d}",
                )

    def set_closed_sum(self):
        """Установить производство равным объему покупок."""
        for p in self.all_products:
            self.model += pulp.lpSum(self.production[p]) == pulp.lpSum(
                self.requirement[p]
            )

    def _cost_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины затрат на производство в деньгах."""
        for p, prod in self.production.items():
            for x in prod.values():
                yield x * self.plant.unit_costs[p]

    @property
    def costs(self):
        return pulp.lpSum(self._cost_items())

    def _sales_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины продаж в деньгах."""
        for p, orders in self.order_dict.items():
            accept = self.accept_dict[p]
            for i, order in enumerate(orders):
                yield order.volume * order.price * accept[i]

    @property
    def sales(self):
        return pulp.lpSum(self._sales_items())

    def inventory_items(self, m: Union[float, None] = None):
        """Штраф за хранение запасов, для целевой функции."""
        m = m if (m is not None) else self.inventory_penalty
        xs = [m * self.inventory[p][d] for p in self.all_products for d in self.days]
        return pulp.lpSum(xs)

    def set_objective(self):
        self.model += self.sales - self.costs - self.inventory_items()

    def solve(self):
        self.feasibility = self.model.solve()

    def evaluate_orders(self, order_dict):
        self.add_orders(order_dict)
        self.set_non_negative_inventory()
        self.set_closed_sum()
        self.set_objective()
        self.solve()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    def default_filename(self):
        return self.name.lower().replace(" ", "_") + ".lp"

    def save(self, filename: str = ""):
        fn = filename if filename else self.default_filename()
        self.model.writeLP(fn)
        print(f"Мы сохранили модель в файл {fn}")

    def order_status(self, p: Product):
        res = []
        for order, status in zip(self.order_dict[p], self.accept_dict[p].values()):
            x = order.__dict__
            x["accepted"] = True if status.value() == 1 else False
            res.append(x)
        return sorted(res, key=lambda x: x["day"])

    def order_status_all(self):
        return {p: self.order_status(p) for p in self.all_products}

    def obj_value(self):
        return pulp.value(self.model.objective)


# Функции для просмотра результатов


def collect(orders: List[Order], days: List):
    acc = [0 for _ in days]
    for order in orders:
        acc[order.day] += order.volume
    return acc


def demand_dict(m: PlantModel):
    return {p: collect(orders, m.days) for p, orders in m.order_dict.items()}


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


def get_values(m):
    return dict(
        all_products=m.all_products,
        demand=demand_dict(m),
        order_status=m.order_status_all(),
        capacity=m.plant.capacity,
        capacity_list=m.daily_capacity(),
        prod=evaluate_vars(m.production),
        ship=evaluate_expr(m.purchases),
        int_use=evaluate_expr(m.internal_use),
        req=evaluate_expr(m.requirement),
        inv=evaluate_expr(m.inventory),
        n_days=max(m.days) + 1,
        sales=m.sales.value(),
        costs=m.costs.value(),
        obj=m.obj_value(),
        status=m.status,
    )


def summary_df(v):
    prop = df(
        {
            "capacity": df(v["capacity_list"]).sum(),
            "orders": df(v["demand"]).sum(),
            "purchase": df(v["ship"]).sum(),
            "internal_use": df(v["int_use"]).sum(),
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


if __name__ == "__main__":
    N_DAYS: int = 14

    # создаем заказы
    orders_a = generate_orders(
        n_days=N_DAYS,
        total_volume=1.35 * 200 * N_DAYS,
        sizer=Volume(min_order=100, max_order=300, round_to=20),
        pricer=Price(mean=150, delta=30),
    )
    orders_b = generate_orders(
        n_days=N_DAYS,
        total_volume=0.8 * 100 * N_DAYS,
        sizer=Volume(min_order=50, max_order=120, round_to=5),
        pricer=Price(mean=200, delta=15),
    )
    order_dict: OrderDict = {Product.A: orders_a, Product.B: orders_b}

    # описываем производство
    unit_a = Unit(Product.A, capacity=200, unit_cost=70, storage_days=2)
    unit_b = Unit(
        Product.B, capacity=100, unit_cost=40, storage_days=2, requires={Product.A: 1.1}
    )
    plant1 = Plant([unit_a, unit_b])

    # модель
    m1 = PlantModel("Two products model aloh_py", n_days=N_DAYS, plant=plant1)
    m1.evaluate_orders(order_dict)
    m1.save()

    # вывести результаты
    print_solution(m1)
