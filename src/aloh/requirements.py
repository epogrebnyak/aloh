"""Direct and full material requirements."""

from dataclasses import dataclass
from typing import List

import numpy as np  # type: ignore
import pandas as pd


def as_dataframe(x, names):
    return pd.DataFrame(x, columns=names, index=names)


def rounds(arr, eps=0.001):
    ix = np.abs(arr) < eps
    arr[ix] = 0
    return arr


def calculate_full_requirement(B):
    n = B.shape[0]
    I = np.identity(n)
    R = np.linalg.inv(I - B)
    return rounds(R)


@dataclass
class Materials:
    product_names: List[str]

    def __post_init__(self):
        """
        B - матрица прямых затрат.
        На производство единицы товара i необходимо B(i,j) единиц товара j.
        """
        self.B = as_dataframe(0, self.product_names)

    def require(self, p_i: str, x: float, p_j: str):
        self.B.loc[p_i, p_j] = x

    def calculate_R(self):
        """
        R - матрица полных затрат.
        """
        return calculate_full_requirement(self.B)

    @property
    def R(self):
        return as_dataframe(self.calculate_R(), self.product_names)

    def requirements_factory(self):
        """Предоставить функцию, которая будет рассчитывать
        полные потребности в продуктах для продукта *p*.
        """

        def req(p: str):
            return g(p, self.product_names, self.calculate_R())

        return req


def g(product: str, products: List[str], R: np.ndarray):
    xs = [(1 if (p == product) else 0) for p in products]
    xs = np.array(xs)
    res = np.matmul(xs, R)
    return {p: r for p, r in zip(products, res)}
