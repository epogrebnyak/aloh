from interface import Product 
from small import OptModel, product_dataframe, orders_dataframe

pa = Product(name="A", capacity=10, unit_cost=0.1, storage_days=1)
pa.add_order(day=0, volume=7, price=0.2)
pa.add_order(day=0, volume=7, price=0.3)
pa.add_order(day=1, volume=10, price=0.09)
pa.add_order(day=2, volume=6, price=0.25)
pa.add_order(day=2, volume=6, price=0.25)

m = OptModel(products=[pa], model_name="model0", inventory_weight=0)
ac, xs = m.evaluate()


def test_0():
    assert ac == {"A": [0, 1, 0, 1, 1]}
    assert xs == {"A": [7, 2, 10]}

df_a = product_dataframe("A", m)
df_orders = orders_dataframe("A", m)

print("Product", "A")
print(df_a, "\n")
print(df_orders)
