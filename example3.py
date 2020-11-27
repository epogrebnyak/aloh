from aloh import Plant, Machine, Product
from aloh import generate_orders, Volume, Price, OrderBook
from aloh import OptModel, print_solution, get_values


plant4 = Plant(
    [
        #Machine(Product.A, capacity=4320, unit_cost=293.6, storage_days=1),
        Machine(
            Product.B,
            capacity=3600,
            unit_cost=340.3,
            storage_days=1,
         #   requires={Product.A: 1},
        ),
        #Machine(
        #    Product.C,
        #    capacity=2160,
        #    unit_cost=430.1,
        #    storage_days=7,
        #    requires={Product.B: 1.37},
        #),
        #Machine(Product.D, capacity=3300, unit_cost=815.1, storage_days=7),
    ]
)

expected_price = [400, 500, 1100, 900]
N_DAYS = 10
order_book = OrderBook(
    {
        #Product.A: generate_orders(
        #    n_days=N_DAYS,
        #    total_volume=0 * 4320 * N_DAYS,
        #    sizer=Volume(min_order=50, max_order=100, round_to=10),
        #    pricer=Price(mean=400, delta=40),
        #),
        Product.B: generate_orders(
            n_days=N_DAYS,
            total_volume=1.1 * 3600 * N_DAYS,
            sizer=Volume(min_order=50, max_order=100, round_to=5),
            pricer=Price(mean=500, delta=50),
        ),
        #Product.C: generate_orders(
        #    n_days=N_DAYS,
        #    total_volume=1.1 * 2160 * N_DAYS,
        #    sizer=Volume(min_order=100, max_order=200, round_to=5),
        #    pricer=Price(mean=1100, delta=110),
        #),
        #Product.D: generate_orders(
        #    n_days=N_DAYS,
        #    total_volume=1.1 * 3300 * N_DAYS,
        #    sizer=Volume(min_order=50, max_order=100, round_to=5),
        #    pricer=Price(mean=900, delta=90),
        #),
    }
)

m= OptModel(
    "Four products model example 3", N_DAYS, order_book, plant4, inventory_penalty=1.5)
from time import perf_counter
start = perf_counter()
m.evaluate()
end = perf_counter()
print_solution(m)
print ("Время:", round(end-start,2), "сек")
