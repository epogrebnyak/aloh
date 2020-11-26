from aloh import (
    Product,
    Dimension,
    generate_orders,
    Volume,
    Price,
    OrderBook,
    Plant,
    Unit,
    PlantModel,
    print_solution,
)


N_DAYS: int = 14
dims = Dimension(n_days=14, products=Product)

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
ob = OrderBook(dims, order_dict)

# описываем производство
unit_a = Unit(Product.A, capacity=200, unit_cost=70, storage_days=2)
unit_b = Unit(
    Product.B, capacity=100, unit_cost=40, storage_days=2, requires={Product.A: 1.1}
)
plant1 = Plant(dims, [unit_a, unit_b])

# модель
m1 = PlantModel(
    "Two products model aloh_py", n_days=N_DAYS, plant=plant1, inventory_penalty=0.1
)
m1.evaluate_orders(order_dict)
m1.save()
a1, p1 = m1.orders_accepted(), m1.production_values()
