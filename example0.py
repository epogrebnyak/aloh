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

N_DAYS = 14

# создаем заказы
orders_a = generate_orders(
    n_days=N_DAYS,
    total_volume=1.35 * 200 * N_DAYS,
    sizer=Volume(min_order=100, max_order=300, round_to=20),
    pricer=Price(mean=150, delta=30),
)
orders_b = generate_orders(
    n_days=N_DAYS,
    total_volume=0.8 * 100 * N_DAYS,
    sizer=Volume(min_order=50, max_order=120, round_to=5),
    pricer=Price(mean=200, delta=15),
)
order_dict = {Product.A: orders_a, Product.B: orders_b}
ob = OrderBook(order_dict)

# описываем производство
mac_a = Machine(Product.A, capacity=200, unit_cost=70, storage_days=2)
mac_b = Machine(
    Product.B, capacity=100, unit_cost=40, storage_days=2, requires={Product.A: 0.8}
)
pt = Plant([mac_a, mac_b])

# модель и решение
om = OptModel(
    "Two products model exmaple0",
    n_days=14,
    order_book=ob,
    plant=pt,
    inventory_penalty=0.1,
)
a, p = om.evaluate()

# вывести результаты
print_solution(om)
vs = get_values(om)
