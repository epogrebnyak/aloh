import numpy as np
import pandas as pd


product_names = ["A (H)", "B (H10)", "C (TA-HSA-10)", "D (TA-240)"]
max_capacity = [4.32, 3.6, 2.16, 3.3]
max_days_storage = [14, 14, 7, 7]
unit_cost = np.array([293.6, 340.3, 430.1, 815.1])
expected_price = np.array([400, 500, 1100, 900])
margin = expected_price - unit_cost

df = pd.DataFrame(
    dict(
        max_capacity=max_capacity,
        unit_cost=unit_cost,
        max_days_storage=max_days_storage,
        expected_price=expected_price,
    ),
    index=product_names,
)
df["margin"] = ((df.expected_price - df.unit_cost) / df.expected_price).round(2)

df.T.to_markdown()
