import pytest

from aloh import DataframeViewer, OptModel
from aloh.interface import Product, get_materials

pa = Product("A")
pa.capacity = 10
pa.unit_cost = 0.1
pa.storage_days = 1
pa.add_order(day=0, volume=1, price=50)
pa.requires = dict(B=0.8, C=1)

pb = Product("B")
pb.capacity = 10
pb.unit_cost = 0.1
pb.storage_days = 1
pb.add_order(day=0, volume=0, price=0)
pb.requires = dict(C=0.5)

pc = Product("C")
pc.capacity = 10
pc.unit_cost = 0.1
pc.storage_days = 1
pc.add_order(day=0, volume=0, price=0)

m = OptModel([pa, pb, pc], model_name="Product depenedencies", inventory_weight=0)
ac, xs = m.evaluate()

print("Orders:", m.accepted_orders())
print("Production:", m.estimated_production())

ms = get_materials([pa, pb, pc])

dv = DataframeViewer(m)
prod_df, ship_df, req_df, inv_df, sales_df, cost_df = dv.inspect_variables()


def test_req_func():
    f = ms.make_req_func()
    assert f("A") == {"A": 1, "B": 0.8, "C": 1.4}
    assert f("B") == {"A": 0, "B": 1, "C": 0.5}
    assert f("C") == {"A": 0, "B": 0, "C": 1}


def test_R_matrix():
    assert ms.R.to_dict() == {
        "A": {"A": 1.0, "B": 0.0, "C": 0.0},
        "B": {"A": 0.8, "B": 1.0, "C": 0.0},
        "C": {"A": 1.4, "B": 0.5, "C": 1.0},
    }


def test_products_with_dependencies():
    assert ac == {"A": [1], "B": [0], "C": [0]}
    assert xs == {"A": [1], "B": [0.8], "C": [1.4]}
