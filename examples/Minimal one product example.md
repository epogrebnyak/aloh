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




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>x</th>
      <th>ship</th>
      <th>inv</th>
      <th>sales</th>
      <th>costs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>7.0</td>
      <td>7.0</td>
      <td>0.0</td>
      <td>2.1</td>
      <td>0.7</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2.0</td>
      <td>0.0</td>
      <td>2.0</td>
      <td>0.0</td>
      <td>0.2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10.0</td>
      <td>12.0</td>
      <td>0.0</td>
      <td>3.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



#### Order selection 

*accept=1* indicates accepted order.


```python
 m.orders_dataframe("A")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>day</th>
      <th>volume</th>
      <th>price</th>
      <th>accept</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>7</td>
      <td>0.20</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>7</td>
      <td>0.30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>10</td>
      <td>0.09</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>6</td>
      <td>0.25</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>6</td>
      <td>0.25</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>


