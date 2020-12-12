# Моделирование выбора заказов и объемов производства

## Документация

https://epogrebnyak.github.io/aloh3/

## Запуск  

```console
set PYTHONIOENCODING=utf8  
git clone https://github.com/epogrebnyak/aloh
cd aloh
pip install _requirements.txt  
pip install -e .
```

## Примеры

### Простой пример - формулировка задачи.
 
Один продукт "A", три дня, пять заказов. Выбрать заказы и объем производства по дням.

```python
from aloh import OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.1, storage_days=1)
pa.add_order(day=0, volume=7, price=0.2)     # менее выгодный заказ
pa.add_order(day=0, volume=7, price=0.3)     # более выгодный заказ, берем
pa.add_order(day=1, volume=10, price=0.09)   # убыточный заказ, не берем
pa.add_order(day=2, volume=6, price=0.25)    # } если есть возможность хранения, 
pa.add_order(day=2, volume=6, price=0.25)    # } берем оба заказа

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()
```

    Solved in 0.099 sec
    

#### План производства, отгрузка, запасы

Производство (*x*), поставки (*ship*), запасы (_inv_) - в натуральном выражении,
продажи (*sales*) and затраты (*costs*) - в денежном выражении.


```python
m.product_dataframe("A")
```

| day |   x |  ship |  inv |  sales |  costs |
|:---:|:---:|:-----:|:----:|:------:|:------:|
|   0 |   7 |     7 |    0 |    2.1 |    0.7 |
|   1 |   2 |     0 |    2 |    0   |    0.2 |
|   2 |  10 |    12 |    0 |    3   |    1   |



#### Выбор заказов

*accept=1* показывает принятый заказ.


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
