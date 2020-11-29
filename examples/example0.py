"""
Пример с двумя связанными продуктами.
Состав заказов: фиксированный 
Дней: 14
"""
from time import perf_counter
from aloh import Plant, Machine
from aloh import generate_orders, Volume, Price, OrderBook
from aloh import OptModel, print_solution, get_values

products = ["A", "B"]
n_days = 28
order_book = OrderBook(products, n_days)
order_book["A"] = generate_orders(
    n_days=n_days,
    total_volume=1.35 * 200 * n_days,
    sizer=Volume(min_order=100, max_order=300, round_to=20),
    pricer=Price(mean=150, delta=30),
)
order_book["B"] = generate_orders(
    n_days=n_days,
    total_volume=0.8 * 100 * n_days,
    sizer=Volume(min_order=50, max_order=120, round_to=5),
    pricer=Price(mean=200, delta=15),
)

plant = Plant(products, n_days)
plant["A"] = Machine(capacity=200, unit_cost=70, storage_days=2)
plant["B"] = Machine(capacity=100, unit_cost=40, storage_days=2, requires={"A": 1.25})


ex0 = OptModel(
    "Two products model dynamic example0 py", order_book, plant, inventory_penalty=1.5
)

start = perf_counter()
a, p = ex0.evaluate()
end = perf_counter()
ex0.save()
print_solution(ex0)
vs = get_values(ex0)


print("\nКоличество заказов:", len(order_book))
print("Дней:", n_days)
print("Продуктов:", len(products))
print("\nВремя:", round(end - start, 2), "сек")
