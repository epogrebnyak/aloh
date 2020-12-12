from interface import Order, Product, make_dataset

pa = Product("A")
pa.capacity = 100
pa.unit_cost = 0.25
pa.add_order(day=5, volume=99, price=0.50)

pb = Product("B")
pb.capacity = 50
pb.unit_cost = 0.15
pb.storage_days = 3
pb.add_order(2, 49, 0.30)


def test_pa():
    assert pa == Product(
        name="A",
        capacity=100,
        unit_cost=0.25,
        storage_days=None,
        orders=[Order(day=5, volume=99, price=0.5)],
        requires={},
    )


def test_storage():
    from copy import copy

    px = copy(pa)
    px.storage_days = 5
    assert px.storage_days == 5


def test_pb():
    assert pb == Product(
        name="B",
        capacity=50,
        unit_cost=0.15,
        storage_days=3,
        orders=[Order(day=2, volume=49, price=0.3)],
        requires={},
    )


def test_dataset_invocation():
    ds = make_dataset([pa, pb])
