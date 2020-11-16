from sim_orders import Product, Order, MultiProductModel, evaluate_vars
from numpy import mean

order_dict_1 = {
    Product.A: [
        Order(day=6, volume=220.0, price=135.3),
        Order(day=6, volume=160.0, price=125.5),
        Order(day=3, volume=240.0, price=158.3),
        Order(day=1, volume=280.0, price=150.9),
        Order(day=5, volume=140.0, price=159.7),
        Order(day=4, volume=280.0, price=167.4),
        Order(day=9, volume=180.0, price=135.6),
        Order(day=7, volume=200.0, price=159.8),
        Order(day=0, volume=220.0, price=129.6),
        Order(day=2, volume=200.0, price=177.1),
        Order(day=7, volume=200.0, price=126.1),
        Order(day=5, volume=180.0, price=172.0),
        Order(day=2, volume=140.0, price=129.0),
        Order(day=0, volume=60.0, price=130.7),
    ],
    Product.B: [
        Order(day=5, volume=90.0, price=35.9),
        Order(day=1, volume=90.0, price=48.6),
        Order(day=0, volume=115.0, price=52.7),
        Order(day=4, volume=115.0, price=36.1),
        Order(day=4, volume=105.0, price=53.1),
        Order(day=8, volume=5.0, price=56.8),
    ],
}


N_DAYS = 10
capacity_dict = {Product.A: 200.0, Product.B: 100.0}

# Определение модели
mp = MultiProductModel("Two products", n_days=N_DAYS, all_products=Product)
mp.set_daily_capacity(capacity_dict)
mp.add_orders(order_dict_1)
mp.set_non_negative_inventory()
mp.set_closed_sum()
mp.set_objective()

mp.solve()

cap = mp.capacities()
for p in capacity_dict.keys():
    assert mean(cap[p]) == capacity_dict[p]

accepted = evaluate_vars(mp.accept_dict)
assert accepted[Product.A] == [
    1.0,
    0.0,
    1.0,
    1.0,
    0.0,
    1.0,
    1.0,
    1.0,
    0.0,
    1.0,
    0.0,
    1.0,
    0.0,
    0.0,
]
assert accepted[Product.B] == [1.0, 1.0, 0.0, 1.0, 1.0, 1.0]
