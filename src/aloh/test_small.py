import pulp
from small import (ProductDict, Order, make_production, multiply, 
                  make_orders, make_shipment_sales, calculate_inventory,
                  lp_sum, values, decisions, dataframes)

inputs = ProductDict()
inputs["A"] = dict(
    capacity=100, unit_cost=35, 
    orders=[Order(0, 70, 50), 
            Order(1, 110, 50), 
            Order(2, 60,  50)]
)
inputs["B"] = dict(
               capacity=200, unit_cost=45, 
               orders=[Order(0, 180, 30), 
                       Order(2, 180, 50)])

n_days = inputs.max_day() + 1
days = list(range(n_days))
products = list(inputs.keys())
capacities = inputs.pick("capacity")
unit_costs = inputs.pick("unit_cost")
order_dict = inputs.pick("orders")

prod = make_production(products, days, capacities)
costs = multiply(unit_costs, prod)
orders = make_orders(order_dict)
ship, sales = make_shipment_sales(products, days, orders)
inv = calculate_inventory(products, days, prod, ship)

model = pulp.LpProblem("Tiny_model", pulp.LpMaximize)
# целевая функция
model += (lp_sum(sales) - lp_sum(costs))
# ограничние 1: неотрицательные запасы
for p in products:
    for d in days:
        model += (
            inv[p][d] >= 0,
            f"Non_negative_inventory_{p}_{d}"
        )        
# ограничние 2: закрытая сумма
for p in products:
    model += pulp.lpSum(prod[p]) == pulp.lpSum(ship[p])

           
model.solve()        
print("Production", values(prod))
print("Orders", decisions(orders))

dfs = dataframes(products, prod, ship, inv, sales, costs)
dfa=dfs['A']
dfb=dfs['B']
print("Продукт A\n", dfa)
print("\nПродукт B\n", dfb)

profit = (dfa.sales - dfa.costs + dfb.sales - dfb.costs).sum()
assert profit >= model.objective.value()
assert (dfa.x - dfa.ship).sum() == 0
assert (dfb.x - dfb.ship).sum() == 0
assert (dfa.inv >= 0).all()
assert (dfb.inv >= 0).all()
assert (dfa.x <= capacities["A"]).all()
assert (dfb.x <= capacities["B"]).all()
assert (dfa.x >= 0).all()
assert (dfb.x >= 0).all()
assert decisions(orders) == {'A': [1, 1, 1], 'B': [0, 1]}

# TODO:
# - prod_df
# - storage_days
# - inventory penalty
# - total requirements