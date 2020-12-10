import pulp

from collections import UserDict
from dataclasses import dataclass

class ProductDict(UserDict):
    pass

    def pick(self, key):
        return {k: v[key] for k, v in self.items()}
    
    def max_day(self):
        return max([order.day for k in self.keys() for order in self[k]['orders']])


def empty(products, days):
    return {p: {d: 0 for d in days} for p in products}


def multiply(vec, mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = vec[p] * mat[p][d]
    return res

def accum(var, i):
    return pulp.lpSum([var[k] for k in range(i + 1)])

def lp_sum(mat):
    return pulp.lpSum([mat[p][d] for p in mat.keys() for d in mat[p].keys()])

def values(mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = pulp.value(mat[p][d])
    return res

@dataclass
class Order:
    """Параметры заказа."""

    day: int
    volume: float
    price: float

@dataclass
class OrderDecision:

    order: Order
    accept: int = 0
    
    def sales(self):
        return self.accept * self.order.volume * self.order.price 

    def ship(self):
        return self.accept * self.order.volume
    
    def value(self):
        return int(self.accept.value())
    

def make_production(products, days, capacities):
    prod = empty(products, days)
    for p in products:
        cap = capacities[p]
        for d in days:
            prod[p][d] = pulp.LpVariable(f"Prod_{p}_{d}", lowBound=0, upBound=cap)
    return prod

def make_orders(order_dict):    
    orders = {}
    for p in order_dict.keys():
        orders[p] = []
        for i, order in enumerate(order_dict[p]):
            accept = pulp.LpVariable(f"Accept_{p}_{i}", cat="Binary")
            od = OrderDecision(order, accept) 
            orders[p].append(od)
    return orders

def make_shipment_sales(products, days, orders):
    ship = empty(products, days)
    sales = empty(products, days)
    for p in products:
      for order in orders[p]:
         for d in days:
            if order.order.day == d:
                ship[p][d] += order.ship()
                sales[p][d] += order.sales()
    return ship, sales            

def calculate_inventory(products, days, prod, ship):
    inv = empty(products, days)
    for p in products:
        xs = prod[p]
        ys = ship[p]
        for d in days:
            inv[p][d] = accum(xs, d) - accum(ys, d)
    return inv   

def decisions(orders):
    return {p:[int(order.accept.value()) for order in orders[p]] for p in orders.keys()}


import pandas as pd

def to_dataframe(p, prod, ship, inv, sales, costs):
    df = pd.DataFrame() 
    df['x'] = series(prod, p)
    df['ship'] = series(ship, p)
    df['inv'] = series(inv, p)
    df['sales'] = series(sales, p)
    df['costs'] = series(costs, p)
    return df

def dataframes(products, prod, ship, inv, sales, costs):
    dfs = {}
    for p in products:
        dfs[p] = to_dataframe(p, prod, ship, inv, sales, costs)
    return dfs

def series(var, p):
    return values(var)[p].values() 

