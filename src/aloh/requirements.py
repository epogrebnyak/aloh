"""Direct and full material requirements."""

from dataclasses import dataclass
from typing import List

import numpy as np  # type: ignore
import pandas as pd


@dataclass
class Materials:
    products: List[str]

    def __post_init__(self):
        """
        B - матрица прямых затрат.
        На производство единицы товара i необходимо B(i,j) единиц товара j.
        """
        self.B = self._dataframe(0)

    def require(self, p_i: str, x: float, p_j: str):
        self.B.loc[p_i, p_j] = x

    def _dataframe(self, x):
        return pd.DataFrame(x, columns=self.products, index=self.products)

    @staticmethod
    def _round(df, eps=0.001):
        ix = df.abs() < eps
        df[ix] = 0
        return df

    @property
    def R(self):
        """
        R - матрица полных затрат.
        """
        I = np.identity(len(self.products))
        R = np.linalg.inv(I - self.B)
        return self._round(self._dataframe(R))


ms = Materials(["A", "B", "C"])
ms.require("A", 0.8, "B")
ms.require("A", 1, "C")
ms.require("B", 0.5, "C")

ms.B
