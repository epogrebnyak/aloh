from aloh.interface import Product
from aloh.small import DataframeViewer, OptModel

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

m = OptModel([pa, pb], model_name="tiny_model", inventory_weight=0.1)
ac, xs = m.evaluate()
print("Orders:", ac)
print("Production:", xs)

# to use in REPL
dv = DataframeViewer(m)
prod_df, ship_df, req_df, inv_df, sales_df, cost_df = dv.inspect_variables()
dfs = dv.product_dataframes()
print("Продукт A")
print(dfs["A"])
print("Продукт B")
print(dfs["B"])
print("\nSummary dataframe:")
print(dv.summary_dataframe())


def test_orders_are_callable():
    assert dv.orders_summary().any().any()


def test_variables():
    vs = dv.inspect_variables()
    prod_df, ship_df, req_df, inv_df, sales_df, cost_df = vs
    assert len(vs) == 6


def test_product_dataframe_A():
    assert dfs["A"].to_dict() == {
        "x": {0: 55.0, 1: 0.0, 2: 55.0},
        "ship": {0: 55.0, 1: 0.0, 2: 55.0},
        "req": {0: 55.0, 1: 0.0, 2: 55.0},
        "inv": {0: 0.0, 1: 0.0, 2: 0.0},
        "sales": {0: 82.5, 1: 0.0, 2: 88.0},
        "costs": {0: 44.0, 1: 0.0, 2: 44.0},
    }


def test_product_dataframe_properties():
    dfa = dfs["A"]
    dfb = dfs["B"]
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


def test_estimated_production():
    assert m.estimated_production() == xs
    assert m.estimated_production() == {"A": [55, 0, 55], "B": [0, 100, 200]}


def test_accepted_orders():
    assert m.accepted_orders() == ac
    assert m.accepted_orders() == {"A": [1, 0, 1, 0], "B": [0, 1, 1]}


def test_accepted_orders_full():
    assert m.accepted_orders_full() == {
        "A": [
            {"order": {"day": 0, "volume": 55, "price": 1.5}, "accepted": 1},
            {"order": {"day": 1, "volume": 110, "price": 1.5}, "accepted": 0},
            {"order": {"day": 2, "volume": 55, "price": 1.6}, "accepted": 1},
            {"order": {"day": 2, "volume": 55, "price": 1.4}, "accepted": 0},
        ],
        "B": [
            {"order": {"day": 0, "volume": 100, "price": 0.3}, "accepted": 0},
            {"order": {"day": 2, "volume": 150, "price": 0.7}, "accepted": 1},
            {"order": {"day": 2, "volume": 150, "price": 0.8}, "accepted": 1},
        ],
    }


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
