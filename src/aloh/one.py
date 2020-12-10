from typing import Dict

import pandas as pd
import pulp
from pandas import DataFrame as DF
from orderbook import Order


def make_prod(n_days: int, capacity_dict: Dict[str, float]) -> DF:
    days = list(range(n_days))
    df = pd.DataFrame(index=days)
    for p in capacity_dict.keys():
        dict_ = pulp.LpVariable.dict(
            f"Production_{p}", days, lowBound=0, upBound=capacity_dict[p]
        )
        df[p] = pd.DataFrame({p: dict_}, index=days)
    return df


def ordered(_dict, df):
    return [_dict[p] for p in df.columns]


def add(df):
    return pulp.lpSum(df.values.tolist())


def values(df):
    def val(x):
        try:
            return x.value()
        except AttributeError:
            return x

    return df.applymap(val).fillna(0)


def yield_orders(order_dict):
    for p, orders in order_dict.items():
        for order in orders:
            _dict = order.__dict__
            _dict["_product"] = p
            yield _dict


def make_sales_req_dataframes(order_dict):
    order_df = pd.DataFrame(yield_orders(order_dict))
    order_df["accept"] = pd.Series(
        pulp.LpVariable.dicts("AcceptOrder", order_df.index, cat="Binary"),
        index=order_df.index,
    )
    order_df["shipment"] = order_df.accept * order_df.volume
    order_df["sales"] = order_df.accept * order_df.volume * order_df.price
    sales_df = order_df.pivot_table(
        index="day", columns="_product", values="sales", aggfunc=add
    )
    req_df = order_df.pivot_table(
        index="day", columns="_product", values="sales", aggfunc=add
    )
    return sales_df, req_df


order_dict = {
    "A": [
        Order(day=0, volume=160, price=100),
        Order(day=0, volume=5, price=35),
        Order(day=1, volume=60, price=100),
        Order(day=2, volume=160, price=100),
    ],
    "B": [
        Order(day=3, volume=100, price=50),
        Order(day=4, volume=120, price=50),
        Order(day=5, volume=30, price=50),
        Order(day=5, volume=1000, price=50),
    ],
}
products = "AB"
n_days = 6
unit_cost_dict = {"A": 0.5, "B": 0.3}
capacity_dict = {"A": 20, "B": 5}
prod_df = make_prod(6, capacity_dict)
u = ordered(unit_cost_dict, prod_df)
cost_df = u * prod_df
sales_df, req_df = make_sales_req_dataframes(order_dict)

model = pulp.LpProblem("Test prod model", pulp.LpMaximize)
model += add(sales_df)
model.solve()
