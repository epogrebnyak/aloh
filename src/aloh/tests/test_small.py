from interface import Product, make_dataset
from small import OptModel, product_dataframes, values, variable_dataframes

pa = Product("A")
pa.capacity = 100
pa.unit_cost = 0.8
pa.storage_days = 0
pa.add_order(day=0, volume=55, price=1.5)
pa.add_order(day=1, volume=110, price=1.5)  # will not take, over capacity
pa.add_order(day=2, volume=55, price=1.6)  #
pa.add_order(day=2, volume=55, price=1.4)  # will not take this one without storage

pb = Product("B")
pb.capacity = 200
pb.unit_cost = 0.6
pb.storage_days = 3
pb.add_order(day=0, volume=100, price=0.3)  # will not take, loss-making
pb.add_order(day=2, volume=150, price=0.7)
pb.add_order(day=2, volume=150, price=0.8)  # prefer to take, higher margin


ds = make_dataset([pa, pb])
m = OptModel([pa, pb], model_name="tiny_model", inventory_weight=0.1)
ac, xs = m.evaluate()

assert ac == {"A": [1, 0, 1, 0], "B": [0, 1, 1]}
assert xs == {"A": [55, 0, 55], "B": [0, 100, 200]}
prod_df, ship_df, inv_df, sales_df, cost_df = variable_dataframes(m)
dfs = product_dataframes(m)
vs = variable_dataframes(m)


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
    assert (dfa.x <= pa.capacity).all()
    assert (dfb.x <= pb.capacity).all()
    assert (dfa.x >= 0).all()
    assert (dfb.x >= 0).all()
    assert m.accept_orders() == {"A": [1, 0, 1, 0], "B": [0, 1, 1]}


if __name__ == "__main__":
    test_all()
