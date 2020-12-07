from dataclasses import dataclass
from typing import Any, Dict, List

import pulp


@dataclass
class Machine:
    """Станок, машина:        
    capacity - максимальный выпуск (мощность), тонн в день 
    unit_cost - переменная стоимость производства, долл/т
    """

    capacity: float
    unit_cost: float


LpExpression = Any
ProductName = str
StorageDays = Dict[ProductName, int]
ProductParamFloat = Dict[ProductName, float]
Plant = Dict[ProductName, Machine]


@dataclass
class FixedDict:
    products: List[ProductName]

    def __post_init__(self):
        self._dict = {p: None for p in self.products}

    def __setitem__(self, key: ProductName, value):
        if key in self.products:
            self._dict[key] = value
        else:
            raise KeyError(f"Key must be of {self.products}, got {key}")

    def __getitem__(self, key: ProductName):
        return self._dict[key]


def capacities(plant: Plant):
    return {p: m.capacity for p, m in plant.items()}


def unit_costs(plant: Plant):
    return {p: m.unit_cost for p, m in plant.items()}


def production(capacity_dict, n_days: int) -> LpExpression:
    """Создать переменные объема производства, ограничить снизу нулем
       и сверху мощностью."""
    days = list(range(n_days))
    production = {}
    for p, capacity in capacity_dict.items():
        production[p] = pulp.LpVariable.dict(
            f"Production_{p}", days, lowBound=0, upBound=capacity
        )
    return production


def costs(production: LpExpression, unit_cost_dict: ProductParamFloat) -> LpExpression:
    """Элементы расчета величины затрат на производство в деньгах."""
    costs = {}
    for p in production.keys():
        costs[p] = {key: None for key in production[p].keys()}
        for d in costs[p].keys():
            costs[p][d] = production[p][d] * unit_cost_dict[p]
    return costs


def prod_and_cost(plant, n_days) -> (LpExpression, LpExpression):
    capacity_dict = capacities(plant)
    unit_cost_dict = unit_costs(plant)
    prod = production(capacity_dict, n_days)
    cost = costs(prod, unit_cost_dict)
    return prod, cost
