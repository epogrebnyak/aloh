from time import perf_counter
from aloh import (
    Product,
    generate_orders,
    Volume,
    Price,
    OrderBook,
    Plant,
    Machine,
    OptModel,
    print_solution,
    get_values,
)

start = perf_counter()
products = [Product.A, Product.B]
n_days = 90
ob = OrderBook(products, n_days)
ob[Product.A] = generate_orders(
    n_days=n_days,
    total_volume=1.35 * 200 * n_days,
    sizer=Volume(min_order=100, max_order=300, round_to=20),
    pricer=Price(mean=150, delta=30),
)
ob[Product.B] = generate_orders(
    n_days=n_days,
    total_volume=0.8 * 100 * n_days,
    sizer=Volume(min_order=50, max_order=120, round_to=5),
    pricer=Price(mean=200, delta=15),
)

plant = Plant(products, n_days)
plant[Product.A] = Machine(capacity=200, unit_cost=70, storage_days=2)
plant[Product.B] = Machine(
    capacity=100, unit_cost=40, storage_days=2, requires={Product.A: 1.25}
)


ex0 = OptModel(
    "Two products model dynamic example0 py", ob, plant, inventory_penalty=1.5
)

a, p = ex0.evaluate()
ex0.save()
print_solution(ex0)
vs = get_values(ex0)
end = perf_counter()

print("\nКоличество заказов:", len(ob))
print("Дней:", n_days)
print("Продуктов:", len(products))
print("\nВремя:", round(end - start, 2), "сек")
