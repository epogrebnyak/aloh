from generate import Order
from interface import Product
from small import OptModel

# fmt: off
pa = Product("A")
pa.capacity=200
pa.unit_cost=70
pa.storage_days=2
pa.orders = [
    Order(day=0, volume=120, price=123.9),
    Order(day=1, volume=280, price=168.6),
    Order(day=3, volume=180, price=132.2),
    Order(day=3, volume=280, price=161.5),
    Order(day=4, volume=260, price=150.2),
    Order(day=4, volume=140, price=157),
    Order(day=4, volume=120, price=162.7),
    Order(day=4, volume=160, price=169.1),
    Order(day=5, volume=240, price=124.3),
    Order(day=7, volume=100, price=122.6),
    Order(day=7, volume=60, price=124),
    Order(day=7, volume=160, price=171.6),
    Order(day=7, volume=100, price=177.5),
    Order(day=8, volume=260, price=148),
    Order(day=10, volume=220, price=122),
    Order(day=10, volume=100, price=179.2),
    Order(day=11, volume=140, price=129.8),
    Order(day=11, volume=240, price=167.7),
    Order(day=11, volume=260, price=179.7),
    Order(day=13, volume=180, price=124.8),
    Order(day=13, volume=180, price=151.3)]
    
pb = Product("B")             
pb.capacity=100
pb.unit_cost=40
pb.storage_days=5
pb.requires={"A": 1.25}
pb.orders = [
    Order(day=0, volume=100, price=213.9),
    Order(day=1, volume=110, price=202.5),
    Order(day=2, volume=115, price=187.2),
    Order(day=5, volume=75, price=214),
    Order(day=9, volume=65, price=194.1),
    Order(day=9, volume=80, price=199.4),
    Order(day=9, volume=65, price=206),
    Order(day=10, volume=85, price=205.8),
    Order(day=10, volume=80, price=210),
    Order(day=11, volume=70, price=193.3),
    Order(day=11, volume=110, price=203.6),
    Order(day=12, volume=65, price=201.5),
    Order(day=12, volume=100, price=204.6)]
# fmt: on

ex1 = OptModel(
    [pa, pb],
    model_name="Two products, fixed orders, 14 days model",
    inventory_weight=1.5,
)
a, p = ex1.evaluate()
