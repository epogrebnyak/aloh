from generate import Order
from interface import product
from small import OptModel, product_dataframes, values, variable_dataframes

# fmt: off
ps = dict()
ps["A"] = product(
    capacity=100,
    unit_cost=0.8,
    storage_days=0,
    orders=[Order(day=0, volume=55, price=1.5),  # will not take, over capacity
            Order(day=1, volume=110, price=1.5), 
            Order(day=2, volume=55, price=1.6),  # under storage=0 can take just one
            Order(day=2, volume=55, price=1.4)], # under storage=0 can take just one
)
ps["B"] = product(
    capacity=200, 
    unit_cost=0.6, 
    storage_days=3,
    orders=[Order(day=0, volume=100, price=0.3), # will not take, loss-making
            Order(day=2, volume=150, price=0.7),
            Order(day=2, volume=150, price=0.8)] # prefer to take, higher margin 
)
m = OptModel(ps, model_name="tiny_model", inventory_weight=0.1)
ac, xs = m.evaluate()
assert ac == {'A': [1, 0, 1, 0], 'B': [0, 1, 1]}
assert xs == {'A': [55, 0, 55], 'B': [0, 100, 200]}
prod_df, ship_df, inv_df, sales_df, cost_df = variable_dataframes(m)
dfs = product_dataframes(m)
vs = variable_dataframes(m)
# fmt: on

print("Production:", values(m.prod))
print("Orders:", m.accept_orders())
print("Продукт A")
print(dfs["A"])
print("Продукт B")
print(dfs["B"])

dfa = dfs["A"]
dfb = dfs["B"]


def test_all():
    assert len(dfa) == 3
    profit = (dfa.sales - dfa.costs + dfb.sales - dfb.costs).sum()
    assert profit >= m.model.objective.value()
    assert (dfa.x - dfa.ship).sum() == 0
    assert (dfb.x - dfb.ship).sum() == 0
    assert (dfa.inv >= 0).all()
    assert (dfb.inv >= 0).all()
    assert (dfa.x <= ps["A"]["capacity"]).all()
    assert (dfb.x <= ps["B"]["capacity"]).all()
    assert (dfa.x >= 0).all()
    assert (dfb.x >= 0).all()
    assert m.accept_orders() == {"A": [1, 0, 1, 0], "B": [0, 1, 1]}


if __name__ == "__main__":
    test_all()
