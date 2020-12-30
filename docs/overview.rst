Overview
========

Products
~~~~~~~~

Suppose we have a manufacturing plant which produces several products (eg. named as `A`, `B`, `C`, `D`, etc).

There is a capacity limit to how much we can produce of each product per day. We also know variable cost of production by product.

Products have limited storage life - they need to be shipped within fixed number of days after production.

The technology to make these products can be chained: for example,
to produce `A` some quantity of `B` is needed, for `B` one needs some 
quantitiy of `C` and `D`, etc.


Planning task
~~~~~~~~~~~~~

At the start the planning period, we know all orders asked for products 
by day, volume and price of shipment. Orders are not confirmed,
our task is to select which ones are feasable and profitable to take.

The calculation task is to determine:

- (a) which orders should be accepted
- (b) production schedule by product and by day

The selection criteria is to maximize profit (sales - production costs) and 
to limit holding of inventory.