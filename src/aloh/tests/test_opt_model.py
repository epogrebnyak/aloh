from interface import Order, Product
from small import OptModel

pa = Product(
    "A",
    capacity=150,
    unit_cost=70,
    orders=[
        # свыше мощности, не берем
        Order(day=0, volume=160, price=100),
        # отрицтельная маржа, не берем
        Order(day=0, volume=5, price=35),
        # берем
        Order(day=1, volume=60, price=100),
        # берем, запасаемся, если хранение позволяет
        Order(day=2, volume=160, price=100),
    ],
)


pb = Product(
    "B",
    capacity=100,
    unit_cost=40,
    orders=[
        # берем
        Order(day=3, volume=100, price=50),
        # берем, если хранение позволяет
        Order(day=4, volume=120, price=50),
        # берем
        Order(day=5, volume=30, price=50),
        # не можем взять, свыше мощности
        Order(day=5, volume=1000, price=50),
    ],
)


def test_model_no_storage_constraint():
    om = OptModel(
        [pa, pb],
        model_name="No_storage_constraint",
        inventory_weight=0.1,
    )

    ac, xs = om.evaluate()
    assert ac == {"A": [0, 0, 1, 1], "B": [1, 1, 1, 0]}
    assert xs == {
        "A": [0.0, 70.0, 150.0, 0.0, 0.0, 0.0],
        "B": [0.0, 0.0, 20.0, 100.0, 100.0, 30.0],
    }


def test_model_with_storage_constraint():
    pa.storage_days = 0
    pb.storage_days = 0
    om = OptModel(
        [pa, pb],
        model_name="With_storage_constraint",
        inventory_weight=0.1,
    )

    ac2, xs2 = om.evaluate()
    assert ac2 == {"A": [0, 0, 1, 0], "B": [1, 0, 1, 0]}
    assert xs2 == {
        "A": [0, 60, 0, 0, 0, 0],
        "B": [0, 0, 0, 100, 0, 30],
    }
