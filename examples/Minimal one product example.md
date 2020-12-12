 ### Example 
 
 One product named "A", three days, five orders. Which order to choose? What is optimal production on each day?


```python
from aloh import OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.1, storage_days=1)
pa.add_order(day=0, volume=7, price=0.2)     # less profitable
pa.add_order(day=0, volume=7, price=0.3)     # more profitable, must take
pa.add_order(day=1, volume=10, price=0.09)   # unprofitable, reject
pa.add_order(day=2, volume=6, price=0.25)    # can accept both with storage
pa.add_order(day=2, volume=6, price=0.25)    # can accept both with storage

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()
```

    Solved in 0.099 sec
    

#### Production schedule

Production (*x*), shipments (*ship*), inventory (_inv_) volumes by day, *sales* and *costs* in money terms. 


```python
m.product_dataframe("A")
```

| day |   x |  ship |  inv |  sales |  costs |
|:---:|:---:|:-----:|:----:|:------:|:------:|
|   0 |   7 |     7 |    0 |    2.1 |    0.7 |
|   1 |   2 |     0 |    2 |    0   |    0.2 |
|   2 |  10 |    12 |    0 |    3   |    1   |



#### Order selection 

*accept=1* indicates accepted order.


```python
 m.orders_dataframe("A")
```

|  n |   day |   volume |   price |   accept |
|:--:|:-----:|:--------:|:-------:|:--------:|
|  0 |     0 |        7 |    0.2  |        0 |
|  1 |     0 |        7 |    0.3  |        1 |
|  2 |     1 |       10 |    0.09 |        0 |
|  3 |     2 |        6 |    0.25 |        1 |
|  4 |     2 |        6 |    0.25 |        1 |

