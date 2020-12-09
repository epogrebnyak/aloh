import pulp

def pick (d, name):
    return {k: v[name] for k,v in d.items()}

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
inputs['A'] = dict(capacity=100, unit_cost=35, 
                   orders=[(0, 100, 50),
                           (1, 150, 50),
                           (2, 150, 50)])
inputs['B'] = dict(capacity=200, unit_cost=45,
                   orders=[(0, 200, 50),
                           (2, 150, 30)]
            )

cap = pick(inputs, 'capacity')
unit_costs = pick(inputs, 'unit_cost')
products = list(inputs.keys())
order_dict = pick(inputs, 'orders')

prod = {}
for p in products:
  for d in days:             
    prod[p] = pulp.LpVariable.dicts("prod", days, lowBound=0, upBound=cap[p])

costs = multiply(unit_costs, prod)

orders = {}
for p in products:
  orders[p] = [(*xs, pulp.LpVariable(f"accept_{i}", cat="Binary") ) 
  for i, xs in enumerate(order_dict[p])]
  
def calc_ship(order):
    return order[1]*order[3]

def calc_sales(order):
    return order[1]*order[2]*order[3]

ship = empty(products, days)
sales = empty(products, days)

for p in products:
     for order in orders[p]:
            for d in days:
               if order[0] == d:
                   sales[p][d] += calc_sales(order)
                   ship[p][d] += calc_ship(order)
                   
                   

