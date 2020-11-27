import pytest
from aloh import Product, Order, Machine, Plant, OrderBook, OptModel, print_solution


def test_plant_assignment():
    p = Plant([Product.A, Product.B], 7)
    p[Product.A] = Machine(capacity=100, unit_cost=10, storage_days=14)
    p[Product.B] = Machine(capacity=120, unit_cost=10, storage_days=14)
    assert list(p.capacity.values()) == [100, 120]


def test_plant_assignment_fails():
    p = Plant([Product.A, Product.B], 7)
    with pytest.raises(KeyError):
        p[Product.C] = Machine(capacity=100, unit_cost=10, storage_days=14)
