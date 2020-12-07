from dataclasses import dataclass
from random import choice, uniform
from typing import List

import pulp

from production import ProductName

# Оптимизационная модель


@dataclass
class Order:
    """Параметры заказа."""

    day: int
    volume: float
    price: float


def make_accept_variables(order_dict):
    """Cоздать бинарные переменные (принят/не принят заказ).
       вида <P>_AcceptOrder_<k>
    """
    accept_dict = {p: dict() for p in order_dict.keys()}
    for p, orders in order_dict.items():
        order_nums = range(len(orders))
        accept_dict[p] = pulp.LpVariable.dicts(
            f"{p}_AcceptOrder", order_nums, cat="Binary"
        )
    return accept_dict


def empty_matrix(n_days, products, x):
    return {p: [x for d in range(n_days)] for p in products}


def get_shipment(n_days, order_dict, accept_dict):
    products = order_dict.keys()
    matrix = empty_matrix(n_days, products, pulp.lpSum(0))
    for p, orders in order_dict.items():
        accept = accept_dict[p]
        for d, _ in enumerate(matrix[p]):
            daily_orders = [
                order.volume * accept[i]
                for i, order in enumerate(orders)
                if d == order.day
            ]
            matrix[p][d] = pulp.lpSum(daily_orders)
    return matrix


def get_sales(n_days, order_dict, accept_dict):
    products = order_dict.keys()
    matrix = empty_matrix(n_days, products, pulp.lpSum(0))
    for p, orders in order_dict.items():
        accept = accept_dict[p]
        for d, _ in enumerate(matrix[p]):
            daily_sales = [
                order.volume * accept[i] * order.price
                for i, order in enumerate(orders)
                if d == order.day
            ]
            matrix[p][d] = pulp.lpSum(daily_sales)
    return matrix


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
