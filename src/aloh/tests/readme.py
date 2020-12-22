from aloh import DataframeViewer, OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.2, storage_days=1)
pa.add_order(day=0, volume=7, price=0.3)  # менее выгодный заказ
pa.add_order(day=0, volume=7, price=0.5)  # более выгодный заказ, берем
pa.add_order(day=1, volume=9, price=0.1)  # убыточный заказ, не берем
pa.add_order(day=2, volume=6, price=0.3)  # } если есть возможность хранения,
pa.add_order(day=2, volume=6, price=0.3)  # } берем оба заказа

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()

ac
"""
{'A': [0, 1, 0, 1, 1]}
"""

m.accepted_orders()
"""
{'A': [0, 1, 0, 1, 1]}
"""

m.accepted_orders_full()
"""
{'A':  
 [{'order': {'day': 0, 'volume': 7, 'price': 0.3}, 'accepted': 0},
  {'order': {'day': 0, 'volume': 7, 'price': 0.5}, 'accepted': 1},
  {'order': {'day': 1, 'volume': 9, 'price': 0.1}, 'accepted': 0},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1}
  ]}
"""

xs
"""
{'A': [7, 2, 10]}
"""

m.estimated_production()
"""
{'A': [7, 2, 10]}
"""

v = DataframeViewer(m)
v.product_dataframe("A")
"""
      x  ship  inv  sales  costs
0   7.0   7.0  0.0    3.5    1.4
1   2.0   0.0  2.0    0.0    0.4
2  10.0  12.0  0.0    3.6    2.0
"""

v.orders_dataframe("A")
"""
   day  volume  price  accept
0    0       7    0.3       0
1    0       7    0.5       1
2    1       9    0.1       0
3    2       6    0.3       1
4    2       6    0.3       1
"""
