import pytest
from aloh import Order, Machine, Plant, OrderBook, OptModel


def test_plant_assignment():
    plant = Plant(["A", "B"], 7)
    plant["A"] = Machine(capacity=100, unit_cost=10, storage_days=14)
    plant["B"] = Machine(capacity=120, unit_cost=10, storage_days=14)
    assert list(plant.capacity.values()) == [100, 120]


def test_plant_assignment_fails():
    plant = Plant(["A", "B"], 7)
    with pytest.raises(KeyError):
        plant["C"] = Machine(capacity=100, unit_cost=10, storage_days=14)


def test_end_to_end():
    products = ["A", "B"]
    n_days = 14
    order_book = OrderBook(products, n_days)
    order_book["A"] = [
        Order(day=7, volume=100.0, price=177.5),
        Order(day=11, volume=240.0, price=167.7),
        Order(day=3, volume=180.0, price=132.2),
        Order(day=4, volume=160.0, price=169.1),
        Order(day=7, volume=100.0, price=122.6),
        Order(day=0, volume=120.0, price=123.9),
        Order(day=13, volume=180.0, price=151.3),
        Order(day=4, volume=140.0, price=157.0),
        Order(day=10, volume=100.0, price=179.2),
        Order(day=3, volume=280.0, price=161.5),
        Order(day=13, volume=180.0, price=124.8),
        Order(day=4, volume=260.0, price=150.2),
        Order(day=5, volume=240.0, price=124.3),
        Order(day=1, volume=280.0, price=168.6),
        Order(day=11, volume=140.0, price=129.8),
        Order(day=7, volume=160.0, price=171.6),
        Order(day=8, volume=260.0, price=148.0),
        Order(day=11, volume=260.0, price=179.7),
        Order(day=4, volume=120.0, price=162.7),
        Order(day=10, volume=220.0, price=122.0),
        Order(day=7, volume=60.0, price=124.0),
    ]
    order_book["B"] = [
        Order(day=2, volume=115.0, price=187.2),
        Order(day=11, volume=110.0, price=203.6),
        Order(day=5, volume=75.0, price=214.0),
        Order(day=9, volume=80.0, price=199.4),
        Order(day=12, volume=65.0, price=201.5),
        Order(day=9, volume=65.0, price=194.1),
        Order(day=1, volume=110.0, price=202.5),
        Order(day=10, volume=80.0, price=210.0),
        Order(day=0, volume=100.0, price=213.9),
        Order(day=10, volume=85.0, price=205.8),
        Order(day=12, volume=100.0, price=204.6),
        Order(day=11, volume=70.0, price=193.3),
        Order(day=9, volume=65.0, price=206.0),
    ]

    plant = Plant(products, n_days)
    plant["A"] = Machine(capacity=200, unit_cost=70, storage_days=2)
    plant["B"] = Machine(
        capacity=100, unit_cost=40, storage_days=5, requires={"A": 1.25}
    )

    ex1 = OptModel(
        "Two products, fixed orders, 14 days model",
        order_book,
        plant,
        inventory_penalty=1.5,
    )
    a, p = ex1.evaluate()
    assert a == dict(
        A=[
            1.0,
            1.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
        ],
        B=[0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
    )

    assert p == dict(
        A=[
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            200.0,
            180.0,
        ],
        B=[0.0, 0.0, 0.0, 0.0, 0.0, 75.0, 0.0, 0.0, 0.0, 80.0, 80.0, 65.0, 100.0, 0.0,],
    )
