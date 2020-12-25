![](https://github.com/epogrebnyak/aloh/workflows/pytest/badge.svg)

# Modeling order selection and production volumes

The `aloh` package allows you to select the most profitable orders and optimize discrete production by day.

#### What is the algorithm?

We solve mixed linear integer programming problem ([MILP][milp]).

[milp]: https://en.wikipedia.org/wiki/Integer_programming

- Received orders are assigned a binary variable (taken or not taken),
  production volumes are continuous variables from zero to maximum output.
- Optimization is carried out in order to maximize profits and reduce product inventory in the warehouse.
- We also take into account the limitations on the shelf life of the product in the warehouse.

#### How do we decide?

To formulate a linear programming problem usint the package [PuLP][pulp], the solution is sought using open solvers such as [CBC] [cbc]. 

[pulp]: https://coin-or.github.io/pulp/
[cbc]: https://github.com/coin-or/Cbc

Possible alternatives to PuLP:

- [Google OR Tools](https://developers.google.com/optimization) 
- [mip-python](https://www.python-mip.com)
- [pyomo](http://www.pyomo.org)
- [JuMP]()

#### Where does the name come from?

The package name is `aloh` - short for the chemical formula of aluminum hydroxide, a demo of production optimization.

## Examples

### 1. A simple example
 
#### 1.1. Statement of the problem

One product ("A"), three-day scheduling, five orders. It is necessary to select profitable orders and production volume by day

The portfolio contains orders that cannot be fulfilled (insufficient production capacity), unprofitable orders (the price is below the cost price) and orders with different margins. Using the algorithm, we select those orders that, firstly, are possible and, secondly, profitable to execute.

```python
from aloh import OptModel, Product

pa = Product(name="A", capacity=10, unit_cost=0.2, storage_days=1)
                                            # Ожидаемые результаты: 
pa.add_order(day=0, volume=7, price=0.3)    # - менее выгодный заказ
pa.add_order(day=0, volume=7, price=0.5)    # - более выгодный заказ, берем
pa.add_order(day=1, volume=9, price=0.1)    # - убыточный заказ, не берем
pa.add_order(day=2, volume=6, price=0.3)    # } - если есть возможность хранения, 
pa.add_order(day=2, volume=6, price=0.3)    # } - берем оба заказа

m = OptModel(products=[pa], model_name="model_0", inventory_weight=0)
ac, xs = m.evaluate()
```

    Solved in 0.099 sec
    
#### 1.2. Selection of orders

As a result of selection, we get the values ​​of binary variables,
relevant recommendations for the order (accept / reject).
   
```python
>>> ac
{'A': [0, 1, 0, 1, 1]}
```

In the expanded view, we see the original order data.

*accept=1* shows accepted order, `0` - declined

```python
>>> m.accepted_orders_full()

{'A': [{'order': {'day': 0, 'volume': 7, 'price': 0.3}, 'accepted': 0},
  {'order': {'day': 0, 'volume': 7, 'price': 0.5}, 'accepted': 1},
  {'order': {'day': 1, 'volume': 9, 'price': 0.1}, 'accepted': 0},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1},
  {'order': {'day': 2, 'volume': 6, 'price': 0.3}, 'accepted': 1}]}
```

The same information in the form of a dataframe

```python
>>> v = DataframeViewer(m)
>>> v.orders_dataframe("A")
   day  volume  price  accept
n                            
0    0       7    0.3       0
1    0       7    0.5       1
2    1       9    0.1       0
3    2       6    0.3       1
4    2       6    0.3       1
```

#### 1.3. Production plan

Production (*x*), deliveries (*ship*), total demand c taking into account internal consumption (*req*), stocks (_inv_) - in kind, sales (*sales*) and costs (*costs*) - in monetary terms.

Short Result:

```python
>>> xs
{'A': [7.0, 2.0, 10.0]}
```

Extended presentation of the result:

```python
>>> v.product_dataframe("A")
        x  ship   req  inv  sales  costs
day                                     
0     7.0   7.0   7.0  0.0    3.5    1.4
1     2.0   0.0   0.0  2.0    0.0    0.4
2    10.0  12.0  12.0  0.0    3.6    2.0
```

## Documentation


https://epogrebnyak.github.io/aloh/

## Installation

Directly from the repo:


```console
pip install --upgrade git+https://github.com/epogrebnyak/aloh.git
```

For development:

```console
git clone https://github.com/epogrebnyak/aloh.git 
cd aloh 
pip install -e .
```

For Windows you may need the command:

```console
set PYTHONIOENCODING=utf8  
```
