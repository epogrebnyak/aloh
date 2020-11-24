"""
### Материальные затраты

> Сколько нужно тонн продукта исходного сырья для производства 1 тонны H?

 1,064 тонны

> Сколько нужно тонн продукта H для производства 1 тонны H10?

1 тонна 

> Сколько нужно тонн продукта H10 для производства 1 тонны TA-HSA-10?

1,37 тонны

> Сколько нужно тонн продукта исходного сырья для производства 1 тонны TA-240?

1,49 тонны 

"""

product_names = ["A (H)", "B (H10)", "C (TA-HSA-10)", "D (TA-240)"]

content_r_in_a = 1.064
content_a_in_b = 1
content_b_in_c = 1.37
content_r_in_d = 1.49

"""
    r     a     b     c     d
r       1.064              1.49
a               1
b                    1.37
c
d
"""

import pandas as pd
import numpy as np

names = "r a b c d".split()
b = pd.DataFrame(0, columns=names, index=names)
b.loc["a", "r"] = 1.064
b.loc["d", "r"] = 1.49
b.loc["b", "a"] = 1
b.loc["c", "b"] = 1.49

r = np.linalg.inv(np.identity(5) - b)
print(r)
