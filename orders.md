# Заказы

- Заявка на покупку принимается в формате `(продукт, цена, день поставки, количество)`

- Каждая заявка покупателя либо принимается, либо отклоняется.

- Мы можем генерировать условный портфель заявок или использовать готовый набор заявок.

    
## Пример кода

```python
from aloh import generate_orders, Volume, Price

N_DAYS = 14
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
order_dict: OrderDict = {Product.A: orders_a, Product.B: orders_b}
```

```python
>> order_dict
Out[2]: 
{<Product.A: 'H'>: [Order(day=4, volume=300.0, price=162.0),
  Order(day=7, volume=140.0, price=121.0),
  Order(day=4, volume=180.0, price=151.3),
  Order(day=12, volume=300.0, price=130.5),
  Order(day=13, volume=120.0, price=137.9),
  Order(day=10, volume=280.0, price=178.1),
  Order(day=2, volume=220.0, price=163.1),
  Order(day=12, volume=260.0, price=153.2),
  Order(day=0, volume=140.0, price=157.6),
  Order(day=0, volume=160.0, price=125.2),
  Order(day=1, volume=200.0, price=152.6),
  Order(day=4, volume=300.0, price=123.8),
  Order(day=13, volume=200.0, price=164.4),
  Order(day=11, volume=140.0, price=172.4),
  Order(day=9, volume=200.0, price=175.5),
  Order(day=5, volume=280.0, price=140.0),
  Order(day=10, volume=160.0, price=137.5),
  Order(day=9, volume=200.0, price=172.2)],
 <Product.B: 'H10'>: [Order(day=7, volume=115.0, price=201.3),
  Order(day=7, volume=85.0, price=202.4),
  Order(day=5, volume=110.0, price=203.4),
  Order(day=1, volume=95.0, price=186.9),
  Order(day=5, volume=100.0, price=209.2),
  Order(day=11, volume=70.0, price=203.3),
  Order(day=3, volume=60.0, price=200.6),
  Order(day=0, volume=75.0, price=185.3),
  Order(day=6, volume=60.0, price=192.9),
  Order(day=4, volume=100.0, price=202.0),
  Order(day=9, volume=90.0, price=202.0),
  Order(day=7, volume=50.0, price=192.2),
  Order(day=12, volume=85.0, price=205.2),
  Order(day=9, volume=25.0, price=211.6)]}
```
