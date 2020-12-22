"""Select orders and plan discrete daily production for several products.

Use *Product* class to formulate input information and *OptModel* to solve 
linear programming model. 

*DataframeViewer* shows modelling results as pandas dataframes.

*generate_orders*, *Price*, *Volume* are used for order simulation.
"""
from .generate import Price, Volume, generate_orders
from .interface import Product
from .small import DataframeViewer, OptModel
