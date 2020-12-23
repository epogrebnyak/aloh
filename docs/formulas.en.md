# Mathematical formulation

v2020.12.23

## Scenario

Suppose we have a manufacturing plant which produces several products (eg. named as `A`, `B`, `C`, `D`, etc).

The technology to make these products can be chained: for example to produce `A` some quantity of 
`B` is needed, for `B` one needs some quantitiy of `C` and `D`, etc. 

Products have limited storage life - they need to be shipped within some time frame after production.

There is a capacity limit to how much we can produce of each product per day.

At the start the planning period, we kbow all orders for  products to be shipped by day and price of shipment. 

The calculation task is to (a) determine which orders should be accepted or rejected and (b) determine the production schedule by product by day in order to maximize the profit and limit inventory.

## Model overview

- A binary variable (0 or 1) assigned to identify whether to accept or reject a order.

- Shipments are the accepted orders. Shipments in dollar terms are sales.

- The daily production volume has a maximum capacity.

- Direct requirements for producing each product are given (intermediate use).

- The daily requirement is shipment plus intermediate use.

- The inventory (stock) is the cumulative production minus the cumulative requrement. Inventory measured end of day.

- Inventory stocks are non-negative.

- The volume of the warehouse is not limited.

- The shelf life of each product is limited.

- The objective is to maximize the profit (sales - cost).

- We also add a penalty for holding the inventory into objective.

## 0. Dimensions (Time and Products)

**0.1** We solve the task of order selection and production scheduling with in $n_{days}$


$$
t = 1, ... n_{days}
$$

Note: in Python implementation we the first index is zero.

**0.2** Let `p` denote index of product. For 4 products we shall have:

$$
p \in [A, B, C, D]
$$

## 1. Production, Shipping, Stock

### 1.1 Production 


$prod_{pt}$  - Production volume of product _p_ per day, tons 

Production volume is the output of solving the optimization problem (maximize profit).

Cost are calculated based on production volume. We account for variable costs, linearly. 

$$
costs = \sum_p \sum_t  prod_{pt} \cdot unit\_cost_p
$$

### 1.2 Shipment


$ship_{pt}$ - shipment of product p per day, tons


Calculated based on selected order (see. below)

<!-- ### 1.3 Intermediate consumption

$use_{pt}$ - demand for the product p tonne/day, needed for the production of other products
$use_{pt}$ - потребность в продукте _p_ в день _t_, тонн, для нужд производства других продуктов

-->

### 1.3 Total requirement

$req_{pt}$ - required volume using product p per day, tons

It is calculated based on the total requirement  matrix. The calculation is described [here](https://github.com/epogrebnyak/aloh3/issues/2). 

$B_{ij}$ - the number of units of product $j$, required for the production of product i (direct cost matrix)

$R_{ij}$ - the number of units of product $j$, directly or indirectly required for the release of a unit of $i$ (total costs matrix).

$R = (I-B)^{-1}$


If $y = [y_A, y_B, y_C, y_D]$ is a row vector with the quantity of each product to sell,
then $x = yR$ is the total output of each product, taking into account internal consumption.

$$
\forall t: req_{t} = ship_{t}^T \cdot R
$$



### 1.5 Inventory (stocks)

$inventory_{pt}$ - stocks of product _p_ at the end of the day, tons

Stocks are defined as the difference between the accumulated amount of production and the accumulated use. Amount of use is requirment from above. Stocks are registered end of day.

$$inventory_{pt} = cumsum(prod, t) - cumsum(req, t)$$

$$cumsum(x_t, t^*) = \sum_{t=1}^{t^*}x_{t}$$

## 2. Orders

###  2.1 Order data structure

The plant receives $n_{orders}$ orders for various products for the entire planning period:

$$order_k = [product_k, day_k, volume_k, price_k]$$

$$k = 1, ... n_{orders}$$

Each order contains (_k_ - order number):

- product $ product_k $ that is ordered
- delivery volume $ volume_k $ (tons)
- day of delivery $ day_k $
- delivery price $ price_k $ (USD per ton)


### 2.2  Order selection variables

A binary variable _accept_ is created for each order, which shows
decision to accept the order or not:

$$
accept_k \in (0, 1)
$$

### 2.3 Calculations based on orders

Supply volume:

$$
ship_{pt} = \sum_{k\vert_{day_k=t}^{product_k = p}}accept_k \cdot volume_k
$$

Volume of sales:

$$
sales = \sum_k accept_k \cdot volume_k  \cdot  price_k
$$

## 3. Limitations

### 3.1 Capacity

Daily production volume is non-negative and is limited from above by capacity

$$0 \leq prod_{pt} \leq capacity_p$$

### 3.2  Non-negative stocks

$$inventory_{pt} \geq 0$$

### 3.3 Closed amount for the period

The production amount is equal to the shipment amount for each product:

$$\forall p: \sum_t prod_{pt} = \sum_t req_{pt} $$

Commentary: perhaps this limitation becomes insignificant after the introduction of restrictions on minimizing stocks.

### 3.4 Limited storage time

Inventory per day _d_ must not exceed product usage for the next $s_p$ days, where $s_p$ is the maximum shelf life p of the product in stock.

First case:

$$ inventory_{pd} \le \sum_{t = d+1}^{d+s_p} req_{pt}, s_p \ge 1 $$

The storage period s = 1 can be substituted into the this inequality, then the stock balance should not exceed the volume of the next day of use ($ req_ {p, d + 1} $).

Second case:

$$ inventory_{pd} = 0, if s_p = 0 $$

Key words: shelf life, product life.

## 4. Objective function

$$(sales - costs - \lambda \cdot inventory)\to max$$

$\lambda \cdot inventory$ - penalty to minimize inventory. $\lambda$ is less than the price of the product.

## 5. Calculation result

- $prod_{pt}$ - production volume by day
- $accept_{k}$ - binary variables for order selection

## Possible changes

 - different options for target functions
 - matrix notation
 - product production time more than 1 day
 - the weights for the stock penalty are proportional to the price
 