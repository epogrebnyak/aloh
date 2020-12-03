# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:58:02 2020

@author: Евгений
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np

products = ["A", "B"]


@dataclass(frozen=True)
class Product:
    name: str


@dataclass
class Machine:
    """Станок, машина:        
    capacity - максимальный выпуск, т в день (мощность)
    unit_cost - переменная стоимость производства, долл/т
    """

    capacity: float
    unit_cost: float


Storage = Dict[Product, int]
Requirements = List[Tuple[Product, float, Product]]
Plant = Dict[Product, Machine]


def require(one_unit_of: Product, requires_x: float, units_of: Product):
    return one_unit_of, requires_x, units_of


def direct_requirement_matrix(products: List[Product]):
    """
    B - матрица прямых затрат.
    На производство единицы товара i необходимо B(i,j) единиц товара j.
    """

    names = [p.name for p in products]
    return pd.DataFrame(0, columns=names, index=names)


import pandas as pd


@dataclass
class Materials:
    products: List[Product]

    def __post_init__(self):
        self.B = self._dataframe(0)

    def _dataframe(self, arr):
        names = [p.name for p in self.products]
        return pd.DataFrame(arr, columns=names, index=names)

    @staticmethod
    def _round(df, eps=0.001):
        ix = df.abs() < eps
        df[ix] = 0
        return df

    def require(self, p1, x, p2):
        self.B.loc[p1, p2] = x
        return self

    @property
    def R(self):
        """
        R - матрица полных затрат.
        """
        I = np.identity(len(self.products))
        R = np.linalg.inv(I - self.B)
        return self._round(self._dataframe(R))


products = [Product("A"), Product("B")]
storage = {Product("A"): 2, Product("B"): 5}
requirements = [require(Product("B"), 1.25, Product("A"))]
plant = {
    Product("A"): Machine(capacity=200, unit_cost=70),
    Product("B"): Machine(capacity=100, unit_cost=40),
}


ps = [
    Product("car"),
    Product("wheel"),
    Product("body"),
    Product("metal"),
    Product("rubber"),
]
ms = Materials(ps).require("car", 1, "body")
ms.require("car", 4, "wheel")
ms.require("wheel", 10, "metal")
ms.require("body", 1500, "metal")
ms.require("body", 50, "rubber")
ms.require("wheel", 7.5, "rubber")
print(ms.R)
