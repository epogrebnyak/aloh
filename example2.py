from aloh import Plant, Machine, Product
from aloh import generate_orders, Volume, Price, OrderBook
from aloh import OptModel, print_solution, get_values
from time import perf_counter

products = [Product.A, Product.B, Product.C, Product.D]
n_days = 60

# Заказы
ob = OrderBook(products, n_days)
ob[Product.A] = generate_orders(
    n_days=n_days,
    total_volume=1.2 * 4320 * n_days,
    sizer=Volume(min_order=1000, max_order=2000, round_to=10),
    pricer=Price(mean=400, delta=40),
)
ob[Product.B] = generate_orders(
    n_days=n_days,
    total_volume=1.2 * 3600 * n_days,
    sizer=Volume(min_order=1000, max_order=2000, round_to=10),
    pricer=Price(mean=500, delta=50),
)
ob[Product.C] = generate_orders(
    n_days=n_days,
    total_volume=1.2 * 2160 * n_days,
    sizer=Volume(min_order=1000, max_order=2000, round_to=10),
    pricer=Price(mean=1100, delta=110),
)
ob[Product.D] = generate_orders(
    n_days=n_days,
    total_volume=1.2 * 3300 * n_days,
    sizer=Volume(min_order=1000, max_order=2000, round_to=10),
    pricer=Price(mean=900, delta=90),
)

# Завод
plant = Plant(products, n_days)
plant[Product.A] = Machine(capacity=4320, unit_cost=293.6, storage_days=14)
plant[Product.B] = Machine(
    capacity=3600, unit_cost=340.3, storage_days=14, requires={Product.A: 1.25}
)
plant[Product.C] = Machine(capacity=2160, unit_cost=430.1, storage_days=7)
plant[Product.D] = Machine(capacity=3300, unit_cost=815.1, storage_days=7)

# Модель
m = OptModel(
    "Four products model dynamic example0 py", ob, plant, inventory_penalty=1.5
)
start = perf_counter()
a, p = m.evaluate()
end = perf_counter()
m.save()
print_solution(m)
vs = get_values(m)
print("\nВремя:", round(end - start, 2), "сек")
