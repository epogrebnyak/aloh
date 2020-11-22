"""Выбор заказов и расчетов объемов производства по нескольким продуктам.

Условия
-------

1. Химическое производство выпускает несколько продуктов, обозначенных A, B, C, D.

2. Объемы производства каждого продукта ограничены максимальным выпуском в день (мощность).

3. Мы выбираем временной период планирования в днях, например, 7, 10, 30 или 60 дней.

4. Мы генерируем условный портфель заказов по продуктам на этот период. Заказы 
   в сумме могут быть больше или меньше суммарной мощности. Индивидуальные заказы
   могут быть меньше или больше мощности производства по дням.

5. Каждый заказ содержит: 

   - день поставки продукта
   - объем поставки в тоннах
   - цену приобретения  

6. Цель расчетов - определить:
    
   - какие заказы выбрать
   - объем производства каждого продукта по дням

7. Целевая функция - максимизация прибыли. По мере усложнения задачи 
   может учитывать другие критерии (например, стоимость запасов).

Математическая модель
---------------------

Описание математической модели на [Сolab](https://colab.research.google.com/drive/1Wf39KC496IZcLDSNRpAEu1w-NfzeMSHu?usp=sharing).

Текущие допущения
-----------------
    
- нет ограничения по срокам хранения продуктов
- стоимость хранения нулевая
- емкость хранения не ограничена
- производство продуктов не связано друг с другом
- нулевые остатки продуктов в начале и конце периода 
- все заказы известны в начале периода
- заказ берется или отклоняется, не пересматривается
  https://github.com/epogrebnyak/aloh3/issues/1
- целевая функция - максимизация выручки    
 
Особенности реализации 
----------------------

- в PuLP задача проще формулируется по строкам, чем по матрице.
- элементы класса Product (перечислимый тип с обозначением продуктов) 
  используются как ключи словарей с данными по продуктам
- в модели оптимизации данные организованы как словари по продуктам (характерно для PuLP)
- методы для получения решения задачи - методы класса, просмотр результатов - отдельные функции
- мы создаем гипотетический портфель заказом и прогнояем модель по нему

"""
import warnings
from dataclasses import dataclass
from enum import Enum
from random import choice, uniform
from typing import Dict, List, Generator

import pandas as pd  # type: ignore
import pulp  # type: ignore

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


# Оптимизационная модель


@dataclass
class Unit:
    product: Product
    capacity: float
    unit_cost: float
    storage_days: int
    requires: ProductParamDict


def accumulate(var, i) -> LpExpression:
    return pulp.lpSum([var[k] for k in range(i + 1)])


class PlantModel:
    obj = pulp.LpMaximize

    def __init__(self, name: str, n_days: int, units: List[Unit]):
        self.units = units
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))
        self.all_products = [u.product for u in units]
        assert len(set(self.all_products)) == len(self.all_products)
        self._init_production()
        self.purchases = self._create_expressions_dict()
        self.requirement = self._create_expressions_dict()
        self.inventory = self._create_expressions_dict()

    def _create_expressions_dict(self) -> DictOfExpressionLists:
        return {p: [pulp.lpSum(0) for d in self.days] for p in self.all_products}

    @property
    def storage_days(self):
        return {u.product: u.storage_days for u in self.units}

    @property
    def unit_costs(self):
        return {u.product: u.unit_cost for u in self.units}

    @property
    def capacity(self):
        return {u.product: u.capacity for u in self.units}

    def _init_production(self):
        """Создать переменные объема производства, ограничить снизу нулем 
           и сверху мощностью."""
        self.production = {}
        for p, cap in self.capacity.items():
            # создаем переменные вида Production_<P>_<d>
            self.production[p] = pulp.LpVariable.dict(
                f"Production_{p.name}", self.days, lowBound=0, upBound=cap
            )

    def _cost_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины затрат на производство в деньгах."""
        for p, prod in self.production.items():
            for x in prod.values():
                yield x * self.unit_costs[p]

    @property
    def costs(self):
        return pulp.lpSum(self._cost_items())

    def add_orders(self, order_dict: OrderDict):
        """Добавить заказы и создать бинарные переменные (принят/не принят заказ.)"""
        self.order_dict = order_dict
        self.accept_dict = {p: dict() for p in self.all_products}
        for p, orders in order_dict.items():
            order_nums = range(len(orders))
            # создаем переменные вида <P>_AcceptOrder_<i>
            self.accept_dict[p] = pulp.LpVariable.dicts(
                f"{p.name}_AcceptOrder", order_nums, cat="Binary"
            )

        """Создать выражения для величины покупок каждого товара в каждый день."""
        for p, orders in order_dict.items():
            accept = self.accept_dict[p]
            for d in self.days:
                daily_orders_sum = [
                    order.volume * accept[i]
                    for i, order in enumerate(orders)
                    if d == order.day
                ]
                self.purchases[p][d] = pulp.lpSum(daily_orders_sum)

        """Создать выражения для общего объема покупок каждого товара."""
        self.requirement = dict()
        for p in self.all_products:
            self.requirement[p] = self.purchases[p].copy()

        """Ввести ограничение на срок складирования продукта."""
        for p in self.all_products:
            s = self.storage_days[p]
            for d in self.days:
                try:
                    self.model += accumulate(self.production[p], d) <= accumulate(
                        self.requirement[p], d + s
                    )
                except IndexError:
                    # Мы не распространяем условие на последние дни периода
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

    def _sales_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины продаж в деньгах."""
        for p, orders in self.order_dict.items():
            accept = self.accept_dict[p]
            for i, order in enumerate(orders):
                yield order.volume * order.price * accept[i]

    @property
    def sales(self):
        return pulp.lpSum(self._sales_items())

    def set_objective(self):
        self.model += self.sales - self.costs

    def solve(self):
        self.feasibility = self.model.solve()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    def save(self, filename: str):
        self.model.writeLP(filename)


class MultiProductModel:
    """Модель с несколькими продуктами.
    
    Задаются переметры (методы add_*):
    - мощности
    - стоимость производства
    - срок хранения 
    - портфель заказов  

    Используются ограничения (методы set_*):
    - неотрицательные остатки
    - сумма производстсва равна сумме потребления за период 
    
    Задается целевая функция (метод set_objective):
    
    Определяются (decision variables):
    - <P>_AcceptOrder_<i> - бинарные переменые брать/не брать i-й заказ на продукт на продукт <P>
    - Production_<P>_<d> - объем производства продукта <P> в день d

    Рассчитываются выражения:
    - inventories - остатки на складе на дням
    - purchases - покупки в натуральном выражении (объем отбора со склада) по дням
    - requirement - общая потребность в товарах на день для отгрузки и для внутреннего использвоания
    - sales_items - продажи, в денежном выражении
    - cost_items - затраты, в денежном выражении
    """

    obj = pulp.LpMaximize

    def __init__(self, name: str, n_days: int, all_products=Product):
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))
        self.all_products = all_products
        # при иницилизации указываем нулевые производственные мощности
        self.production: DictOfExpressionLists = {}
        self.add_daily_capacity({p: 0 for p in all_products})
        # создаем нулевые выражения
        self.purchases: DictOfExpressionLists = self._create_expressions_dict()
        self.requirement: DictOfExpressionLists = self._create_expressions_dict()
        self.inventory: DictOfExpressionLists = self._create_expressions_dict()

    def is_defined(self):
        try:
            self.unit_costs
            self.order_dict
            return True
        except AttributeError:
            return False

    def _create_expressions_dict(self) -> DictOfExpressionLists:
        return {p: [pulp.lpSum(0) for d in self.days] for p in self.all_products}

    def add_unit_cost(self, unit_cost_dict: ProductParamDict):
        self.unit_costs = {p: 0 for p in self.all_products}
        self.unit_costs.update(unit_cost_dict)

    def add_daily_capacity(self, daily_capacity: ProductParamDict):
        """Создать переменные объема производства, ограничить снизу и сверху."""
        for p, cap in daily_capacity.items():
            # создаем переменные вида Production_<P>_<d>
            self.production[p] = pulp.LpVariable.dict(
                f"Production_{p.name}", self.days, lowBound=0, upBound=cap
            )

    @property
    def capacities(self):
        return {
            p: [x.upBound for x in self.production[p].values()]
            for p in self.all_products
        }

    def add_orders(self, order_dict: OrderDict):
        """Добавить заказы и создать бинарные переменные (принят/не принят заказ.)"""
        self.order_dict = {p: [] for p in self.all_products}
        self.order_dict.update(order_dict)
        self.accept_dict = {p: dict() for p in self.all_products}
        for p, orders in order_dict.items():
            order_nums = range(len(orders))
            # создаем переменные вида <P>_AcceptOrder_<i>
            self.accept_dict[p] = pulp.LpVariable.dicts(
                f"{p.name}_AcceptOrder", order_nums, cat="Binary"
            )
        self._init_purchases()
        self._init_requirement()

    def _init_purchases(self):
        """Создать выражения для величины покупок каждого товара в каждый день."""
        for p, orders in self.order_dict.items():
            accept = self.accept_dict[p]
            for d in self.days:
                daily_orders_sum = [
                    order.volume * accept[i]
                    for i, order in enumerate(orders)
                    if d == order.day
                ]
                self.purchases[p][d] = pulp.lpSum(daily_orders_sum)

    def _init_requirement(self):
        """Создать выражения для общего объема покупок каждого товара."""
        for p in self.all_products:
            self.requirement[p] = self.purchases[p].copy()
        # TODO: додавить в requirement объемы внутреннего потребления
        #       например, для продукта B нужно 0.7 тонн продукта А

    def add_max_storage_time(self, storage_time_dict: ProductParamDict):
        """Ввести ограничение на срок складирования продукта."""
        for p in storage_time_dict.keys():
            max_days_storage = storage_time_dict[p]
            for d in self.days:
                try:
                    # Смысл: если мы произведем на дату d товаров больше,
                    #        чем будет приобретено за период d + s
                    #        дней, то не все произведенные товары
                    #        смогут купить. Вводим условие от обратного.
                    self.model += accumulate(self.production[p], d) <= accumulate(
                        self.requirement[p], d + max_days_storage
                    )
                except IndexError:
                    # Мы не распространяем условие на последние дни периода
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

    def sales_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины продаж в деньгах."""
        for p, orders in self.order_dict.items():
            accept = self.accept_dict[p]
            for i, order in enumerate(orders):
                yield order.volume * order.price * accept[i]

    @property
    def sales(self):
        return pulp.lpSum(self.sales_items())

    def cost_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины затрат на производство в деньгах."""
        for p, prod in self.production.items():
            for x in prod.values():
                yield x * self.unit_costs[p]

    @property
    def costs(self):
        return pulp.lpSum(self.cost_items())

    def set_objective(self):
        self.model += self.sales - self.costs

    def solve(self):
        self.feasibility = self.model.solve()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]

    def save(self, filename: str):
        self.model.writeLP(filename)


# Функции для просмотра результатов


def obj_value(m: MultiProductModel):
    return pulp.value(m.model.objective)


def collect(orders: List[Order], days: List):
    acc = [0 for _ in days]
    for order in orders:
        acc[order.day] += order.volume
    return acc


def demand_dict(m: MultiProductModel):
    return {p: collect(orders, m.days) for p, orders in m.order_dict.items()}


def order_status(m: MultiProductModel, p: Product):
    res = []
    for order, status in zip(m.order_dict[p], m.accept_dict[p].values()):
        x = order.__dict__
        x["accepted"] = True if status.value() == 1 else False
        res.append(x)
    return sorted(res, key=lambda x: x["day"])


def evaluate_expr(holder):
    """Получить словарь со значениями выражений"""
    return {p: [item.value() for item in holder[p]] for p in holder.keys()}


def evaluate_vars(holder):
    """Получить словарь со значениями переменных"""
    return {p: [item.value() for item in holder[p].values()] for p in holder.keys()}


def df(dict_, index_name="день"):
    df = pd.DataFrame(dict_)
    df.index.name = index_name
    return df


def print_solution(m):
    dem = demand_dict(m)
    # accepted = evaluate_vars(m.accept_dict)
    prod = evaluate_vars(m.production)
    pur = evaluate_expr(m.purchases)
    inv = evaluate_expr(m.inventory)
    n_days = max(m.days)

    print("\nПериод планирования, дней / Number of days:", n_days)
    print("\nМощности производства, тонн в день: / Capacity, ton per day")
    for k, v in m.capacity.items():
        print("  ", k.name, "-", v)

    print("\nЗаказы")
    for p in Product:
        cd = df(order_status(m, p), "N заказа")
        if not cd.empty:
            print("\nЗаказы на продукт", p.name)
            print(cd)
    print("\nСпрос (тонн) / Demand (ton)")
    print(df(dem))
    print("\nПродажи (тонн) / Purchases (ton)")
    print(df(pur))
    print("\nПроизводство (тонн) / Production (ton)")
    print(df(prod))
    print("\nЗапасы (тонн) / Inventory (ton)")
    print(df(inv))

    print("\nОбъемы мощностей, заказов, производства, покупок (тонн)")
    print("Capacity, orders, production, purchases (ton)\n")
    prop = df(
        {
            # "capacity": df(m.capacity).mean() * n_days,
            "orders": df(demand_dict(m)).sum(),
            "production": df(prod).sum(),
            "purchase": df(pur).sum(),
        },
        "",
    )
    print(prop.T)

    print("\nВыручка (долл.США) / Sales ('000 USD): %0.0f" % mp.sales.value())
    print("Затраты (долл.США) / Costs ('000 USD): %0.0f" % mp.costs.value())
    print("Целевая функция / Target function:     %0.0f" % obj_value(mp))


if __name__ == "__main__":
    N_DAYS: int = 14

    # orders
    orders_a = generate_orders(
        n_days=N_DAYS,
        total_volume=1.35 * 200 * N_DAYS,
        sizer=Volume(min_order=100, max_order=300, round_to=20),
        pricer=Price(mean=150, delta=30),
    )
    orders_b = generate_orders(
        n_days=N_DAYS,
        total_volume=0.52 * 100 * N_DAYS,
        sizer=Volume(min_order=80, max_order=120, round_to=5),
        pricer=Price(mean=50, delta=15),
    )
    order_dict: OrderDict = {Product.A: orders_a, Product.B: orders_b}

    # 1. Данные на входе задачи
    ua = Unit(Product.A, capacity=200, unit_cost=70, storage_days=2, requires={})
    ub = Unit(
        Product.B, capacity=100, unit_cost=40, storage_days=2, requires={Product.B: 1.3}
    )
    pm = PlantModel("Two products model", n_days=N_DAYS, units=[ua, ub])
    pm.add_orders(order_dict)
    pm.set_non_negative_inventory()
    pm.set_closed_sum()
    pm.set_objective()
    pm.solve()

    dem = demand_dict(pm)
    accepted = evaluate_vars(pm.accept_dict)
    prod = evaluate_vars(pm.production)
    pur = evaluate_expr(pm.purchases)
    inv = evaluate_expr(pm.inventory)

    capacity_dict: ProductParamDict = {Product.A: 200, Product.B: 100}
    unit_cost_dict: ProductParamDict = {Product.A: 100 - 30, Product.B: 50 - 10}
    perish_dict = {Product.A: 2, Product.B: 2}

    # 2. Определение модели
    mp = MultiProductModel("Two products model", n_days=N_DAYS, all_products=Product)

    # передаем параметры задачи
    mp.add_daily_capacity(capacity_dict)
    mp.add_unit_cost(unit_cost_dict)
    mp.add_orders(order_dict)
    mp.add_max_storage_time(perish_dict)

    # задаем ограничения
    mp.set_non_negative_inventory()
    mp.set_closed_sum()

    # целевая функция (выражение для нее становится известно в конце блока определения)
    mp.set_objective()

    # 3. Поиск решения для модели
    mp.solve()
    print("\nСтатус решения:", mp.status)

    # 4. Получение данных решения / solution as dictionaries
    dem = demand_dict(mp)
    accepted = evaluate_vars(mp.accept_dict)
    prod = evaluate_vars(mp.production)
    pur = evaluate_expr(mp.purchases)
    inv = evaluate_expr(mp.inventory)

    # 5. Печать решения
    print("\nПериод планирования, дней / Number of days:", N_DAYS)
    print("\nМощности производства, тонн в день: / Capacity, ton per day")
    for k, v in capacity_dict.items():
        print("  ", k.name, "-", v)

    print("\nЗаказы / Orders")
    for p in Product:
        cd = df(order_status(mp, p), "N заказа")
        if not cd.empty:
            print("\nЗаказы на продукт", p.name)
            print(cd)
    print("\nСпрос (тонн) / Demand (ton)")
    print(df(dem))
    print("\nПродажи (тонн) / Purchases (ton)")
    print(df(pur))
    print("\nПроизводство (тонн) / Production (ton)")
    print(df(prod))
    print("\nЗапасы (тонн) / Inventory (ton)")
    print(df(inv))

    print("\nОбъемы мощностей, заказов, производства, покупок (тонн)")
    print("Capacity, orders, production, purchases (ton)\n")
    prop = df(
        {
            "capacity": df(mp.capacities).mean() * N_DAYS,
            "orders": df(demand_dict(mp)).sum(),
            "production": df(prod).sum(),
            "purchase": df(pur).sum(),
        },
        "",
    )
    print(prop.T)

    print("\nВыручка (долл.США) / Sales ('000 USD): %0.0f" % mp.sales.value())
    print("Затраты (долл.США) / Costs ('000 USD): %0.0f" % mp.costs.value())
    print("Целевая функция / Target function:     %0.0f" % obj_value(mp))

    filename = "model_two_product.lp"
    mp.save(filename)
    print(f"\nСохранили модель в файл {filename}")

    def lst(xs):
        return ", ".join(xs)

    from pulp import LpSolverDefault

    print("\nВозможные солверы:", lst(pulp.list_solvers()))
    print("Доступные:  ", lst(pulp.list_solvers(onlyAvailable=True)))
    print("Использован:", LpSolverDefault.name)

    # https://github.com/coin-or/Cbc
    # pulp.get_solver('PULP_CBC_CMD').path
    # https://en.wikipedia.org/wiki/Branch_and_cut
    # https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html

    # TODO:
    # - [x] сохранить модель в тестовый файл формата LP
    # - [x] срок хранения (shelf life)
    # - [x] затраты на производство - умножать на производство (costs of production)
    # - [ ] связанное производство (precursors)
    # - [ ] разные варианты целевых функций (стоимость хранения) - target functions, ввести стоимость запасов
    # - [ ] приблизить к параметрам фактических товаров (more calibration to real data) - см. файл inputs.py

    # FIXME:
    # - [x] почище дефолтные значения сделать - когда нет данных по какому-то продукту
    # - [ ] logging
    # - [x] расссказать про солверы

    # Not todo (сл.этапы, на выдор):
    # - [ ] стек запасов - проверить даты произвосдва запасов на складе.
    # - [ ] web-приложение, кнопки - сгенерировать заказы, изменить параметры, пересчитать https://www.streamlit.io/
    # - [ ] встроить в Эксель через XlWings (https://www.xlwings.org/)
    # - [ ] вывести расчеты в ноутбук Colab
    # - [ ] сделать пакетом
    # - [ ] взять реальные данные за месяц, прогнат на них оптимизацию, посмотреть результат
    # - [ ] визуализации запасов
