import pulp


def pick(d, name):
    return {k: v[name] for k, v in d.items()}


def empty(products, days):
    return {p: {d: 0 for d in days} for p in products}


def multiply(vec, mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = vec[p] * mat[p][d]
    return res


days = [0, 1, 2]
inputs = {}
inputs["A"] = dict(
    capacity=100, unit_cost=35, orders=[(0, 100, 50), (1, 150, 50), (2, 150, 50)]
)
inputs["B"] = dict(capacity=200, unit_cost=45, orders=[(0, 200, 50), (2, 150, 30)])

cap = pick(inputs, "capacity")
unit_costs = pick(inputs, "unit_cost")
products = list(inputs.keys())
order_dict = pick(inputs, "orders")

prod = {}
for p in products:
    for d in days:
        prod[p] = pulp.LpVariable.dicts(f"prod_{p}", days, lowBound=0, upBound=cap[p])

costs = multiply(unit_costs, prod)

from dataclasses import dataclass


@dataclass
class Order:
    """Параметры заказа."""

    day: int
    volume: float
    price: float
    accept: int = 0


orders = {}
for p in products:
    orders[p] = [
        Order(*xs, pulp.LpVariable(f"Accept_{p}_{i}", cat="Binary"))
        for i, xs in enumerate(order_dict[p])
    ]

ship = empty(products, days)
sales = empty(products, days)
for p in products:
 for order in orders[p]:
   for d in days:
      if order.day == d:
            print(order)
            ship[p][d] += order.volume * order.accept
            sales[p][d] += order.volume * order.accept * order.price
            print(p, d, ship)

#        print(ship)

def accum(var, i):
    return pulp.lpSum([var[k] for k in range(i + 1)])

def lp_sum(dict_):
    return pulp.lpSum([dict_[p][d] for p in dict_.keys() for d in dict_[p].keys()])


def values(mat):
    res = {}
    for p in mat.keys():
        res[p] = {}
        for d in mat[p].keys():
            res[p][d] = pulp.value(mat[p][d])
    return res
    

inv = empty(products, days)
for p in products:
    xs = prod[p]
    ys = ship[p]
    for d in days:
        inv[p][d] = accum(xs, d) - accum(ys, d)


model = pulp.LpProblem("Tiny model", pulp.LpMaximize)
model += lp_sum(sales) - lp_sum(costs)
for p in products:
    for d in days:
        model += (
            inv[p][d] >= 0,
            f"Non-negative inventory of {p} at day {d}",
        )
model.solve()        
print(ship)