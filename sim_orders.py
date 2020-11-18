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
CapacityDict = Dict[Product, float]
# FIXME: дает ошибку в проверке mypy
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
        if remaining >= 0:
            xs.append(x)
        else:
            xs.append(total_volume - sum(xs))
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


def accumulate(var, i) -> LpExpression:
    return pulp.lpSum([var[k] for k in range(i + 1)])


class MultiProductModel:
    """Модель с несколькими продуктами.
    
    Определяются (decision variables):
    - <P>_AcceptOrder_<i> - бинарные переменые брать/не брать i-й заказ на продукт на продукт <P>
    - Production_<P>_<d> - объем производства продукта <P> в день d

    Рассчитываются выражения:
    - inventories - остатки на складе на дням
    - purchases - покупки в натуральном выражении (объем отбора со склада) по дням
    - sales_items - продажи, в денежном выражении
    """

    obj = pulp.LpMaximize

    def __init__(self, name: str, n_days: int, all_products=Product):
        self.model = pulp.LpProblem(name, self.obj)
        self.days = list(range(n_days))
        self.all_products = all_products
        # создаем нулевые выражения для покупок и запасов
        self.purchases = self._create_expressions_dict()
        self.inventory = self._create_expressions_dict()
        self.order_dict = {p: [] for p in all_products}
        self.accept_dict = {p: dict() for p in self.all_products}
        # при иницилизации указываем нулевые производственные мощности
        self.production = {}
        self.set_daily_capacity({p: 0 for p in all_products})
        # не создам выражения для заказов, потому что не знаем их количесвто

    def _create_expressions_dict(self):
        return {p: [pulp.lpSum(0) for d in self.days] for p in self.all_products}

    def set_daily_capacity(self, daily_capacity: CapacityDict):
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
        self.order_dict.update(order_dict)
        for p, orders in order_dict.items():
            order_nums = range(len(orders))
            # создаем переменные вида <P>_AcceptOrder_<i>
            self.accept_dict[p] = pulp.LpVariable.dicts(
                f"{p.name}_AcceptOrder", order_nums, cat="Binary"
            )
        self._init_purchases()

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

    def set_non_negative_inventory(self):
        """Установить неотрицательную величину запасов.
           Без этого требования запасы переносятся обратно во времени.
        """
        for p in self.all_products:
            prod = self.production[p]
            pur = self.purchases[p]
            for d in self.days:
                self.inventory[p][d] = accumulate(prod, d) - accumulate(pur, d)
                self.model += (
                    self.inventory[p][d] >= 0,
                    f"Non-negative inventory of {p.name} at day {d}",
                )

    def sales_items(self) -> Generator[LpExpression, None, None]:
        """Элементы расчета величины продаж в деньгах."""
        for p, orders in self.order_dict.items():
            accept = self.accept_dict[p]
            for i, order in enumerate(orders):
                yield order.volume * order.price * accept[i]
                
    def set_max_storage_time(self, storage_time_dict):
        pass             

    # Constraint 3 - "nothing perished" ("условие непротухания")
    # We should not have inventory that would perish (exceed storage time and would
    # not be bought). If we hold inventory greater than expected purshases, at least
    # some inventory will perish.
    # This formulation may change if we allow non-zero end of month stocks.
    # for i in days:
    #     try:
    #         model += inventory(i) <= cumbuy(i + max_days_storage - 1) - cumbuy(i)
    #         # this is mathematically equivalent to:
    #         # cumprod(i) <= cumbuy(i+max_days_storage-1)
    #         # (earlier suggested by Dmitry)
    #     except IndexError:
    #         pass


    def set_closed_sum(self):
        """Установить производство равным объему покупок."""
        for p in self.all_products:
            self.model += pulp.lpSum(self.production[p]) == pulp.lpSum(
                self.purchases[p]
            )

    def set_objective(self):
        self.model += pulp.lpSum(self.sales_items())

    def solve(self):
        self.feasibility = self.model.solve()

    @property
    def status(self):
        return pulp.LpStatus[self.feasibility]


# Функции для просмотра результатов


def sales_value(m: MultiProductModel):
    return pulp.lpSum(m.sales_items()).value()


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


if __name__ == "__main__":

    # 1. Данные на входе задачи         
    N_DAYS: int = 10
    capacity_dict: CapacityDict = {Product.A: 200, Product.B: 100}
    orders_a = generate_orders(
        n_days=N_DAYS,
        total_volume=1.35 * capacity_dict[Product.A] * N_DAYS,
        sizer=Volume(min_order=100, max_order=300, round_to=20),
        pricer=Price(mean=150, delta=30),
    )
    orders_b = generate_orders(
        n_days=N_DAYS,
        total_volume=0.52 * capacity_dict[Product.B] * N_DAYS,
        sizer=Volume(min_order=80, max_order=120, round_to=5),
        pricer=Price(mean=50, delta=15),
    )
    order_dict: OrderDict = {Product.A: orders_a, Product.B: orders_b}

    # 2. Определение модели    
    mp = MultiProductModel("Two products", n_days=N_DAYS, all_products=Product)
    # передаем параметры задачи
    mp.set_daily_capacity(capacity_dict)
    mp.add_orders(order_dict)
    # задаем ограничения 
    mp.set_non_negative_inventory()     # без этого запасы они могут стать отрицательными
    mp.set_closed_sum()                 # без этого или минимизации запасов или функции затрат устанавливается максимальное производство
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
    
    print("\nВыручка (долл.США) / Sales ('000 USD):", sales_value(mp))
    print("Целевая функция: / Target function:   ", obj_value(mp))

    # TODO:
    # - [ ] срок хранения (shelf life)
    # - [ ] связанное производство (precursors)
    # - [ ] затарты на производство - умножать на производство (costs of production)
    # - [ ] разные варианты целевых функций (стоимость хранения) - target functions
    # - [ ] приблизить к параметрам на фактических товаров (more calibration to real data)
