![](https://github.com/epogrebnyak/aloh/workflows/Test_package/badge.svg)

# Моделирование выбора заказов и объемов производства

Пакет `aloh` позволяет оптимизировать дискретное производство и выбрать наиболее выгодные заказы. 
 
#### Что за алгоритм?

Мы решаем задачу смешанного линейного целочисленного программирования ([MILP][milp]). 

[milp]: https://en.wikipedia.org/wiki/Integer_programming

Полученным заказам присваивается бинарная переменная (взяли-не взяли), объемы производства это непрерывные переменные от нуля до максимального выпуска. 
Оптимизация ведется с целью максимизации прибыли и уменьшения запасов продукции на складе. 
Мы также учитываем ограничения на срок хранения продукта на складе. 

#### Чем решаем?

Для формулировки задачи используется пакет [PuLP][pulp], решение ищется с помощью открытых солверов, таких как [CBC][cbc].

[pulp]: https://coin-or.github.io/pulp/
[cbc]: https://github.com/coin-or/Cbc

#### Что такое `aloh`?

`aloh` - сокращение от химической формулы гидроксида алюминия, нашего демонстрационного примера оптимизации производства.


## Примеры

### 1. Простой пример
 
#### 1.1. Формулировка задачи

Один продукт ("A"), планирование на три дня, пять заказов. Необходимо выбрать выгодные заказы и объем производства по дням.

В портфеле есть заказы, которые невозможно выполнить (недостаточно производственных мощностей), невыгодные заказы (цены ниже себестоимости) и заказы с разной 
маржинальностью. Мы выбираем из них заказы, которые, во-первых, возможно и, во-вторых, выгодно выполнить.

```python
from aloh import OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.2, storage_days=1)
pa.add_order(day=0, volume=7, price=0.3)    # менее выгодный заказ
pa.add_order(day=0, volume=7, price=0.5)    # более выгодный заказ, берем
pa.add_order(day=1, volume=9, price=0.1)    # убыточный заказ, не берем
pa.add_order(day=2, volume=6, price=0.3)    # } если есть возможность хранения, 
pa.add_order(day=2, volume=6, price=0.3)    # } берем оба заказа

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()
```

    Solved in 0.099 sec
    
```python
>>> ac
{'A': [0, 1, 0, 1, 1]}

>>> m.accepted_orders()
{'A':  
 [{'order': {'day': 0, 'volume': 7, 'price': 0.3}, 'accepted': 0},
  {'order': {'day': 0, 'volume': 7, 'price': 0.5}, 'accepted': 1},
  {'order': {'day': 1, 'volume': 9, 'price': 0.1}, 'accepted': 0},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1}
 ]
}

>>> m.estimated_production()
{'A': [7.0, 2.0, 10.0]}
```

#### 1.2. План производства, отгрузка, запасы

Производство (*x*), поставки (*ship*), запасы (_inv_) - в натуральном выражении,
продажи (*sales*) and затраты (*costs*) - в денежном выражении.

```python
v = DataframeViewer(m)
v.product_dataframe("A")
```

```
      x  ship  inv  sales  costs
0   7.0   7.0  0.0    3.5    1.4
1   2.0   0.0  2.0    0.0    0.4
2  10.0  12.0  0.0    3.6    2.0
```

#### 1.3. Выбор заказов

*accept=1* показывает принятый заказ.

```python
 v.orders_dataframe("A")
```

```
   day  volume  price  accept
0    0       7    0.3       0
1    0       7    0.5       1
2    1       9    0.1       0
3    2       6    0.3       1
4    2       6    0.3       1
```

## Документация

https://epogrebnyak.github.io/aloh/

## Запуск  

```console
set PYTHONIOENCODING=utf8  
git clone https://github.com/epogrebnyak/aloh
cd aloh
pip install _requirements.txt  
pip install -e .
```
