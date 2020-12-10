from small import ProductDict, Order, values, product_dataframes, variable_dataframes, OptModel

inputs = ProductDict()
inputs["A"] = dict(
    capacity=100,
    unit_cost=35,
    orders=[Order(0, 70, 50), Order(1, 110, 50), Order(2, 60, 50)],
)
inputs["B"] = dict(
    capacity=200, unit_cost=45, orders=[Order(0, 180, 30), Order(2, 180, 50)]
)
m = OptModel(inputs, model_name="tiny_model")
m.evaluate()
print("Production", values(m.prod))
print("Orders", m.accept_orders())

dfs = product_dataframes(m)
dfa = dfs["A"]
dfb = dfs["B"]
print("Продукт A\n", dfa)
print("\nПродукт B\n", dfb)

profit = (dfa.sales - dfa.costs + dfb.sales - dfb.costs).sum()
assert profit >= m.model.objective.value()
assert (dfa.x - dfa.ship).sum() == 0
assert (dfb.x - dfb.ship).sum() == 0
assert (dfa.inv >= 0).all()
assert (dfb.inv >= 0).all()
assert (dfa.x <= inputs["A"]["capacity"]).all()
assert (dfb.x <= inputs["B"]["capacity"]).all()
assert (dfa.x >= 0).all()
assert (dfb.x >= 0).all()
assert m.accept_orders() == {"A": [1, 1, 1], "B": [0, 1]}

prod_df, ship_df, inv_df, sales_df, cost_df = variable_dataframes(m)

# TODO:
# - use OptModel(name, inputs, inventory_weight=0)
# - storage_days
# - inventory penalty
# - total requirements