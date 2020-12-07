import pulp

from opt_model import OptModel
from orderbook import Order
from production import Machine

order_dict = {
    "A": [
        # свыше мощности, не берем
        Order(day=0, volume=160, price=100),
        # отрицтельная маржа, не берем
        Order(day=0, volume=5, price=35),
        # берем
        Order(day=1, volume=60, price=100),
        # берем, запасаемся, если хранение позволяет
        Order(day=2, volume=160, price=100),
    ],
    "B": [
        # берем
        Order(day=3, volume=100, price=50),
        # берем, запасаемся
        Order(day=4, volume=120, price=50),
        # берем, если хранение позволяет
        Order(day=5, volume=30, price=50),
        # не можем взять, свыше мощности
        Order(day=5, volume=1000, price=50),
    ],
}
plant = {
    "A": Machine(capacity=150, unit_cost=70),
    "B": Machine(capacity=100, unit_cost=40),
}


def test_model_no_storage_constraint():
    om = OptModel(
        name="No storage constraint",
        n_days=6,
        products=["A", "B"],
        order_dict=order_dict,
        plant=plant,
        storage_days={"A": 6, "B": 6},
        inventory_penalty=0.1,
        objective_type=pulp.LpMaximize,
        feasibility=0,
    )

    ac, ps = om.evaluate()
    assert ac == {"A": [0, 0, 1, 1], "B": [1, 1, 1, 0]}
    assert ps == {"A": [0, 70, 150, 0, 0, 0], "B": [0, 0, 20, 100, 100, 30]}


def test_model_with_storage_constraint():
    om2 = OptModel(
        name="Storage 0 days, same day consumption",
        n_days=6,
        products=["A", "B"],
        order_dict=order_dict,
        plant=plant,
        storage_days={"A": 0, "B": 0},
        inventory_penalty=0.1,
        objective_type=pulp.LpMaximize,
        feasibility=0,
    )

    ac2, ps2 = om2.evaluate()
    assert ac2 == {"A": [0.0, 0.0, 1.0, 0.0], "B": [1.0, 0.0, 1.0, 0.0]}
    assert ps2 == {
        "A": [0.0, 60.0, 0.0, 0.0, 0.0, 0.0],
        "B": [0.0, 0.0, 0.0, 100.0, 0.0, 30.0],
    }
