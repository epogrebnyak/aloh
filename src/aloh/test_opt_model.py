from opt_model import OptModel
from orderbook import Order
from production import Machine
import pulp


def test_model():
    order_dict = {
        "A": [
            Order(day=0, volume=160, price=100),  # свыше мощности, не берем
            Order(day=0, volume=5, price=35),  # отрицтельная маржа, не берем
            Order(day=1, volume=60, price=100),  # берем
            Order(day=2, volume=160, price=100),
        ],  # берем, запасаемся
        "B": [
            Order(day=3, volume=100, price=50),  # берем
            Order(day=4, volume=120, price=50),  # берем, запасаемся
            Order(day=5, volume=30, price=50),  # берем
            Order(day=5, volume=1000, price=50),
        ],
    }  # не можем взять

    plant = {
        "A": Machine(capacity=150, unit_cost=70),
        "B": Machine(capacity=100, unit_cost=40),
    }

    om = OptModel(
        name="This model",
        n_days=6,
        products=["A", "B"],
        order_dict=order_dict,
        plant=plant,
        storage_days=None,
        inventory_penalty=0.1,
        objective_type=pulp.LpMaximize,
        feasibility=0,
    )

    ac, ps = om.evaluate()
    assert ac == {"A": [0, 0, 1, 1], "B": [1, 1, 1, 0]}
    assert ps == {"A": [0, 70, 150, 0, 0, 0], "B": [0, 0, 20, 100, 100, 30]}
