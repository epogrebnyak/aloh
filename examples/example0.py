"""
Пример с двумя связанными продуктами.
Состав заказов: динамический
"""
from aloh import Product
from aloh import generate_orders, Volume, Price
from aloh import OptModel

n_days = 28

pa = Product("A", capacity=200, unit_cost=70, storage_days=2)
pa.orders = generate_orders(
    n_days=n_days,
    total_volume=1.35 * 200 * n_days,
    sizer=Volume(min_order=100, max_order=300, round_to=20),
    pricer=Price(mean=150, delta=30),
)
pb = Product("B", capacity=100, unit_cost=40, storage_days=2, requires={"A": 1.25})
pb.orders = generate_orders(
    n_days=n_days,
    total_volume=0.8 * 100 * n_days,
    sizer=Volume(min_order=50, max_order=120, round_to=5),
    pricer=Price(mean=200, delta=15),
)

m = OptModel([pa, pb], "Two products model dynamic example0 py", inventory_weight=1.5)

ac, xs = m.evaluate()
of = m.orders_dataframes()
dfs = m.product_dataframes()

print("Количество заказов:", len(of))
print("Дней:", n_days)
print("Продуктов:", 2)
print("Время:", round(m.time_elapsed, 2), "сек")
