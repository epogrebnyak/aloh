from aloh import OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.1, storage_days=1)
pa.add_order(day=0, volume=7, price=0.20)
pa.add_order(day=0, volume=7, price=0.30)
pa.add_order(day=1, volume=9, price=0.09)
pa.add_order(day=2, volume=6, price=0.25)
pa.add_order(day=2, volume=6, price=0.25)

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()

df_a = m.product_dataframes()["A"]
df_orders = m.orders_dataframes()["A"]

print("Product", "A")
print(df_a, "\n")
print(df_orders)


def test_0():
    assert ac == {"A": [0, 1, 0, 1, 1]}
    assert xs == {"A": [7, 2, 10]}
