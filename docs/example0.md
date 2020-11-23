# Пример (aloh.py)

<https://github.com/epogrebnyak/aloh3/blob/main/aloh.py>

```
Название модели: Two products model aloh_py
Мы сохранили модель в файл two_products_model_aloh_py.lp

Статус решения: Optimal

Период планирования, дней: 14

Мощности производства, тонн в день:
  A: 200
  B: 100

Заказы на продукт A
          day  volume  price  accepted
N заказа                              
0           0   120.0  165.4      True
1           0   280.0  170.7     False
2           0   140.0  140.4     False
3           1   140.0  156.6     False
4           1   160.0  149.9     False
5           1   180.0  129.9     False
6           2   160.0  177.3      True
7           2   200.0  173.6      True
8           5   120.0  157.5      True
9           5   120.0  173.9      True
10          6    60.0  175.2      True
11          7   300.0  140.3      True
12          8   180.0  122.2     False
13          8   300.0  137.3     False
14         10   200.0  124.3     False
15         10   200.0  174.3      True
16         11   140.0  138.8      True
17         11   160.0  130.0     False
18         11   120.0  162.4      True
19         11   100.0  137.0      True
20         12   200.0  143.9      True
21         13   200.0  167.0      True

Заказы на продукт B
          day  volume  price  accepted
N заказа                              
0           2    90.0  188.9     False
1           3   110.0  212.3      True
2           4   100.0  197.4      True
3           5    50.0  198.7      True
4           6    65.0  192.5     False
5           6    65.0  194.7      True
6           6    10.0  211.9      True
7           7    55.0  204.2      True
8           7    55.0  191.8      True
9           8   120.0  208.1      True
10          9   105.0  190.8     False
11         10    55.0  214.7      True
12         12    70.0  190.1      True
13         12    95.0  185.6     False
14         12    75.0  188.3     False

Спрос (тонн)
      Product.A  Product.B
день                      
0         540.0        0.0
1         480.0        0.0
2         360.0       90.0
3           0.0      110.0
4           0.0      100.0
5         240.0       50.0
6          60.0      140.0
7         300.0      110.0
8         480.0      120.0
9           0.0      105.0
10        400.0       55.0
11        520.0        0.0
12        200.0      240.0
13        200.0        0.0

Отгрузка (тонн)
      Product.A  Product.B
день                      
0         120.0        0.0
1           0.0        0.0
2         360.0        0.0
3           0.0      110.0
4           0.0      100.0
5         240.0       50.0
6          60.0       75.0
7         300.0      110.0
8           0.0      120.0
9           0.0        0.0
10        200.0       55.0
11        360.0        0.0
12        200.0       70.0
13        200.0        0.0

Производство (тонн)
      Product.A  Product.B
день                      
0         199.0        0.0
1         200.0        0.0
2         200.0       10.0
3         200.0      100.0
4         200.0      100.0
5         200.0       55.0
6         200.0      100.0
7         200.0      100.0
8         200.0      100.0
9         200.0        0.0
10        200.0       55.0
11        200.0        0.0
12        200.0       70.0
13        200.0        0.0

Запасы (тонн)
      Product.A  Product.B
день                      
0          79.0        0.0
1         279.0        0.0
2         119.0       10.0
3         198.0        0.0
4         288.0        0.0
5         193.0        5.0
6         250.5       30.0
7          29.5       20.0
8          97.5        0.0
9         297.5        0.0
10        237.0        0.0
11         77.0        0.0
12          0.0        0.0
13          0.0        0.0

Объемы мощностей, заказов, производства, покупок (тонн)
               Product.A  Product.B
capacity          2800.0     1400.0
orders            3780.0     1120.0
purchase          2040.0      690.0
internal_use       759.0        0.0
requirement       2799.0      690.0
production        2799.0      690.0
avg_inventory      153.2        4.6

Выручка (долл.США):  464636
Затраты (долл.США):  223530
Прибыль (долл.США):  241106

Целевая функция:     240885

Возможные солверы: GLPK_CMD, PYGLPK, CPLEX_CMD, CPLEX_PY, CPLEX_DLL, GUROBI, GUROBI_CMD, MOSEK, XPRESS, PULP_CBC_CMD, COIN_CMD, COINMP_DLL, CHOCO_CMD, PULP_CHOCO_CMD, MIPCL_CMD, SCIP_CMD
Доступные:   PULP_CBC_CMD
Использован: PULP_CBC_CMD
Где находится: D:\Anaconda3\lib\site-packages\pulp\apis\..\solverdir\cbc\win\64\cbc.exe
```

### Работа солвера

```
Welcome to the CBC MILP Solver 
Version: 2.9.0 
Build Date: Feb 12 2015 

command line - D:\Anaconda3\lib\site-packages\pulp\apis\..\solverdir\cbc\win\64\cbc.exe C:\Users\B7E3~1\AppData\Local\Temp\b076792c15614c2bb9d6641e7cb86e86-pulp.mps max ratio None allow None threads None presolve on strong None gomory on knapsack on probing on branch printingOptions all solution C:\Users\B7E3~1\AppData\Local\Temp\b076792c15614c2bb9d6641e7cb86e86-pulp.sol (default strategy 1)
At line 2 NAME          MODEL
At line 3 ROWS
At line 59 COLUMNS
At line 1386 RHS
At line 1441 BOUNDS
At line 1507 ENDATA
Problem MODEL has 54 rows, 65 columns and 1187 elements
Coin0008I MODEL read with 0 errors
String of None is illegal for double parameter ratioGap value remains 0
String of None is illegal for double parameter allowableGap value remains 0
String of None is illegal for integer parameter threads value remains 0
String of None is illegal for integer parameter strongBranching value remains 5
Option for gomoryCuts changed from ifmove to on
Option for knapsackCuts changed from ifmove to on
Continuous objective value is 245120 - 0.00 seconds
Cgl0004I processed model has 50 rows, 64 columns (36 integer (36 of which binary)) and 1078 elements
Cbc0038I Initial state - 4 integers unsatisfied sum - 0.777879
Cbc0038I Pass   1: suminf.    0.19667 (2) obj. -240844 iterations 4
Cbc0038I Pass   2: suminf.    0.00000 (0) obj. -203187 iterations 4
Cbc0038I Solution found of -203187
Cbc0038I Relaxing continuous gives -203202
Cbc0038I Before mini branch and bound, 31 integers at bound fixed and 17 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 14 rows 15 columns
Cbc0038I Mini branch and bound improved solution from -203202 to -232812 (0.01 seconds)
Cbc0038I Freeing continuous variables gives a solution of -232820
Cbc0038I Round again with cutoff of -233872
Cbc0038I Pass   3: suminf.    0.19667 (2) obj. -240844 iterations 0
Cbc0038I Pass   4: suminf.    0.46527 (1) obj. -233872 iterations 3
Cbc0038I Pass   5: suminf.    0.46527 (1) obj. -233872 iterations 0
Cbc0038I Pass   6: suminf.    0.51383 (2) obj. -233872 iterations 8
Cbc0038I Pass   7: suminf.    0.25000 (2) obj. -238184 iterations 2
Cbc0038I Pass   8: suminf.    0.45996 (1) obj. -233872 iterations 3
Cbc0038I Pass   9: suminf.    1.04493 (4) obj. -233872 iterations 16
Cbc0038I Pass  10: suminf.    0.75000 (2) obj. -235120 iterations 4
Cbc0038I Pass  11: suminf.    0.81153 (2) obj. -233872 iterations 2
Cbc0038I Pass  12: suminf.    1.09654 (3) obj. -233872 iterations 13
Cbc0038I Pass  13: suminf.    0.61690 (2) obj. -236452 iterations 3
Cbc0038I Pass  14: suminf.    0.06287 (2) obj. -233872 iterations 3
Cbc0038I Pass  15: suminf.    0.05923 (2) obj. -233872 iterations 1
Cbc0038I Pass  16: suminf.    0.67608 (2) obj. -233872 iterations 4
Cbc0038I Pass  17: suminf.    0.52167 (2) obj. -236668 iterations 2
Cbc0038I Pass  18: suminf.    0.44054 (2) obj. -233872 iterations 3
Cbc0038I Pass  19: suminf.    0.43829 (2) obj. -233872 iterations 1
Cbc0038I Pass  20: suminf.    1.55603 (6) obj. -233872 iterations 22
Cbc0038I Pass  21: suminf.    1.31184 (4) obj. -233872 iterations 4
Cbc0038I Pass  22: suminf.    0.40833 (2) obj. -237125 iterations 6
Cbc0038I Pass  23: suminf.    0.40833 (2) obj. -237125 iterations 0
Cbc0038I Pass  24: suminf.    0.39678 (1) obj. -233872 iterations 4
Cbc0038I Pass  25: suminf.    0.39678 (1) obj. -233872 iterations 0
Cbc0038I Pass  26: suminf.    0.40833 (2) obj. -237861 iterations 2
Cbc0038I Pass  27: suminf.    1.22134 (3) obj. -233872 iterations 15
Cbc0038I Pass  28: suminf.    0.63167 (2) obj. -236308 iterations 1
Cbc0038I Pass  29: suminf.    0.63116 (2) obj. -233872 iterations 2
Cbc0038I Pass  30: suminf.    0.54001 (2) obj. -233872 iterations 1
Cbc0038I Pass  31: suminf.    0.20000 (1) obj. -234605 iterations 2
Cbc0038I Pass  32: suminf.    0.23645 (1) obj. -233872 iterations 3
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 13 integers at bound fixed and 13 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 34 rows 37 columns
Cbc0038I Mini branch and bound improved solution from -232820 to -240239 (0.05 seconds)
Cbc0038I Round again with cutoff of -240861
Cbc0038I Reduced cost fixing fixed 9 variables on major pass 3
Cbc0038I Pass  32: suminf.    0.23952 (2) obj. -241182 iterations 1
Cbc0038I Pass  33: suminf.    0.40175 (1) obj. -240861 iterations 5
Cbc0038I Pass  34: suminf.    0.40175 (1) obj. -240861 iterations 0
Cbc0038I Pass  35: suminf.    0.59000 (2) obj. -240861 iterations 2
Cbc0038I Pass  36: suminf.    1.26552 (5) obj. -240861 iterations 10
Cbc0038I Pass  37: suminf.    1.09458 (4) obj. -240861 iterations 1
Cbc0038I Pass  38: suminf.    0.50651 (3) obj. -240861 iterations 2
Cbc0038I Pass  39: suminf.    0.70020 (3) obj. -240861 iterations 4
Cbc0038I Pass  40: suminf.    0.45699 (3) obj. -240861 iterations 2
Cbc0038I Pass  41: suminf.    0.55548 (3) obj. -240861 iterations 4
Cbc0038I Pass  42: suminf.    0.17011 (2) obj. -240861 iterations 1
Cbc0038I Pass  43: suminf.    0.38952 (2) obj. -242243 iterations 3
Cbc0038I Pass  44: suminf.    0.38952 (2) obj. -242243 iterations 0
Cbc0038I Pass  45: suminf.    0.17011 (2) obj. -240861 iterations 3
Cbc0038I Pass  46: suminf.    1.24849 (5) obj. -240861 iterations 14
Cbc0038I Pass  47: suminf.    0.95271 (3) obj. -240861 iterations 2
Cbc0038I Pass  48: suminf.    0.40952 (2) obj. -241615 iterations 3
Cbc0038I Pass  49: suminf.    0.37355 (2) obj. -240861 iterations 2
Cbc0038I Pass  50: suminf.    0.83814 (2) obj. -240861 iterations 2
Cbc0038I Pass  51: suminf.    0.33785 (2) obj. -240861 iterations 3
Cbc0038I Pass  52: suminf.    0.71447 (3) obj. -240861 iterations 5
Cbc0038I Pass  53: suminf.    0.43619 (2) obj. -241038 iterations 2
Cbc0038I Pass  54: suminf.    0.47604 (2) obj. -240861 iterations 2
Cbc0038I Pass  55: suminf.    0.78864 (3) obj. -240861 iterations 6
Cbc0038I Pass  56: suminf.    0.89619 (3) obj. -240861 iterations 3
Cbc0038I Pass  57: suminf.    0.71086 (2) obj. -240861 iterations 2
Cbc0038I Pass  58: suminf.    0.46629 (2) obj. -240861 iterations 3
Cbc0038I Pass  59: suminf.    0.50801 (3) obj. -240861 iterations 9
Cbc0038I Pass  60: suminf.    0.50801 (3) obj. -240861 iterations 0
Cbc0038I Pass  61: suminf.    0.55363 (2) obj. -240861 iterations 3
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 17 integers at bound fixed and 16 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 32 rows 31 columns
Cbc0038I Mini branch and bound improved solution from -240239 to -240885 (0.06 seconds)
Cbc0038I Round again with cutoff of -241624
Cbc0038I Reduced cost fixing fixed 15 variables on major pass 4
Cbc0038I Pass  61: suminf.    0.26140 (3) obj. -241624 iterations 1
Cbc0038I Pass  62: suminf.    0.66851 (2) obj. -241624 iterations 3
Cbc0038I Pass  63: suminf.    0.15286 (2) obj. -242505 iterations 1
Cbc0038I Pass  64: suminf.    0.14286 (1) obj. -242294 iterations 1
Cbc0038I Pass  65: suminf.    0.93612 (4) obj. -241624 iterations 7
Cbc0038I Pass  66: suminf.    0.16952 (2) obj. -241871 iterations 3
Cbc0038I Pass  67: suminf.    0.60622 (2) obj. -241624 iterations 4
Cbc0038I Pass  68: suminf.    0.60622 (2) obj. -241624 iterations 0
Cbc0038I Pass  69: suminf.    0.16952 (2) obj. -241871 iterations 3
Cbc0038I Pass  70: suminf.    0.59019 (3) obj. -241624 iterations 6
Cbc0038I Pass  71: suminf.    0.38165 (3) obj. -241624 iterations 2
Cbc0038I Pass  72: suminf.    0.33452 (2) obj. -242392 iterations 3
Cbc0038I Pass  73: suminf.    0.38165 (3) obj. -241624 iterations 3
Cbc0038I Pass  74: suminf.    0.30554 (3) obj. -241624 iterations 3
Cbc0038I Pass  75: suminf.    0.35774 (2) obj. -241624 iterations 4
Cbc0038I Pass  76: suminf.    0.15119 (2) obj. -241992 iterations 3
Cbc0038I Pass  77: suminf.    0.60160 (2) obj. -241624 iterations 4
Cbc0038I Pass  78: suminf.    0.60160 (2) obj. -241624 iterations 0
Cbc0038I Pass  79: suminf.    0.15119 (2) obj. -241992 iterations 3
Cbc0038I Pass  80: suminf.    0.86029 (2) obj. -241624 iterations 6
Cbc0038I Pass  81: suminf.    0.86029 (2) obj. -241624 iterations 1
Cbc0038I Pass  82: suminf.    0.37286 (2) obj. -242099 iterations 2
Cbc0038I Pass  83: suminf.    0.35021 (2) obj. -241624 iterations 2
Welcome to the CBC MILP Solver 
Version: 2.9.0 
Build Date: Feb 12 2015 

command line - D:\Anaconda3\lib\site-packages\pulp\apis\..\solverdir\cbc\win\64\cbc.exe C:\Users\B7E3~1\AppData\Local\Temp\b076792c15614c2bb9d6641e7cb86e86-pulp.mps max ratio None allow None threads None presolve on strong None gomory on knapsack on probing on branch printingOptions all solution C:\Users\B7E3~1\AppData\Local\Temp\b076792c15614c2bb9d6641e7cb86e86-pulp.sol (default strategy 1)
At line 2 NAME          MODEL
At line 3 ROWS
At line 59 COLUMNS
At line 1386 RHS
At line 1441 BOUNDS
At line 1507 ENDATA
Problem MODEL has 54 rows, 65 columns and 1187 elements
Coin0008I MODEL read with 0 errors
String of None is illegal for double parameter ratioGap value remains 0
String of None is illegal for double parameter allowableGap value remains 0
String of None is illegal for integer parameter threads value remains 0
String of None is illegal for integer parameter strongBranching value remains 5
Option for gomoryCuts changed from ifmove to on
Option for knapsackCuts changed from ifmove to on
Continuous objective value is 245120 - 0.00 seconds
Cgl0004I processed model has 50 rows, 64 columns (36 integer (36 of which binary)) and 1078 elements
Cbc0038I Initial state - 4 integers unsatisfied sum - 0.777879
Cbc0038I Pass   1: suminf.    0.19667 (2) obj. -240844 iterations 4
Cbc0038I Pass   2: suminf.    0.00000 (0) obj. -203187 iterations 4
Cbc0038I Solution found of -203187
Cbc0038I Relaxing continuous gives -203202
Cbc0038I Before mini branch and bound, 31 integers at bound fixed and 17 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 14 rows 15 columns
Cbc0038I Mini branch and bound improved solution from -203202 to -232812 (0.01 seconds)
Cbc0038I Freeing continuous variables gives a solution of -232820
Cbc0038I Round again with cutoff of -233872
Cbc0038I Pass   3: suminf.    0.19667 (2) obj. -240844 iterations 0
Cbc0038I Pass   4: suminf.    0.46527 (1) obj. -233872 iterations 3
Cbc0038I Pass   5: suminf.    0.46527 (1) obj. -233872 iterations 0
Cbc0038I Pass   6: suminf.    0.51383 (2) obj. -233872 iterations 8
Cbc0038I Pass   7: suminf.    0.25000 (2) obj. -238184 iterations 2
Cbc0038I Pass   8: suminf.    0.45996 (1) obj. -233872 iterations 3
Cbc0038I Pass   9: suminf.    1.04493 (4) obj. -233872 iterations 16
Cbc0038I Pass  10: suminf.    0.75000 (2) obj. -235120 iterations 4
Cbc0038I Pass  11: suminf.    0.81153 (2) obj. -233872 iterations 2
Cbc0038I Pass  12: suminf.    1.09654 (3) obj. -233872 iterations 13
Cbc0038I Pass  13: suminf.    0.61690 (2) obj. -236452 iterations 3
Cbc0038I Pass  14: suminf.    0.06287 (2) obj. -233872 iterations 3
Cbc0038I Pass  15: suminf.    0.05923 (2) obj. -233872 iterations 1
Cbc0038I Pass  16: suminf.    0.67608 (2) obj. -233872 iterations 4
Cbc0038I Pass  17: suminf.    0.52167 (2) obj. -236668 iterations 2
Cbc0038I Pass  18: suminf.    0.44054 (2) obj. -233872 iterations 3
Cbc0038I Pass  19: suminf.    0.43829 (2) obj. -233872 iterations 1
Cbc0038I Pass  20: suminf.    1.55603 (6) obj. -233872 iterations 22
Cbc0038I Pass  21: suminf.    1.31184 (4) obj. -233872 iterations 4
Cbc0038I Pass  22: suminf.    0.40833 (2) obj. -237125 iterations 6
Cbc0038I Pass  23: suminf.    0.40833 (2) obj. -237125 iterations 0
Cbc0038I Pass  24: suminf.    0.39678 (1) obj. -233872 iterations 4
Cbc0038I Pass  25: suminf.    0.39678 (1) obj. -233872 iterations 0
Cbc0038I Pass  26: suminf.    0.40833 (2) obj. -237861 iterations 2
Cbc0038I Pass  27: suminf.    1.22134 (3) obj. -233872 iterations 15
Cbc0038I Pass  28: suminf.    0.63167 (2) obj. -236308 iterations 1
Cbc0038I Pass  29: suminf.    0.63116 (2) obj. -233872 iterations 2
Cbc0038I Pass  30: suminf.    0.54001 (2) obj. -233872 iterations 1
Cbc0038I Pass  31: suminf.    0.20000 (1) obj. -234605 iterations 2
Cbc0038I Pass  32: suminf.    0.23645 (1) obj. -233872 iterations 3
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 13 integers at bound fixed and 13 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 34 rows 37 columns
Cbc0038I Mini branch and bound improved solution from -232820 to -240239 (0.05 seconds)
Cbc0038I Round again with cutoff of -240861
Cbc0038I Reduced cost fixing fixed 9 variables on major pass 3
Cbc0038I Pass  32: suminf.    0.23952 (2) obj. -241182 iterations 1
Cbc0038I Pass  33: suminf.    0.40175 (1) obj. -240861 iterations 5
Cbc0038I Pass  34: suminf.    0.40175 (1) obj. -240861 iterations 0
Cbc0038I Pass  35: suminf.    0.59000 (2) obj. -240861 iterations 2
Cbc0038I Pass  36: suminf.    1.26552 (5) obj. -240861 iterations 10
Cbc0038I Pass  37: suminf.    1.09458 (4) obj. -240861 iterations 1
Cbc0038I Pass  38: suminf.    0.50651 (3) obj. -240861 iterations 2
Cbc0038I Pass  39: suminf.    0.70020 (3) obj. -240861 iterations 4
Cbc0038I Pass  40: suminf.    0.45699 (3) obj. -240861 iterations 2
Cbc0038I Pass  41: suminf.    0.55548 (3) obj. -240861 iterations 4
Cbc0038I Pass  42: suminf.    0.17011 (2) obj. -240861 iterations 1
Cbc0038I Pass  43: suminf.    0.38952 (2) obj. -242243 iterations 3
Cbc0038I Pass  44: suminf.    0.38952 (2) obj. -242243 iterations 0
Cbc0038I Pass  45: suminf.    0.17011 (2) obj. -240861 iterations 3
Cbc0038I Pass  46: suminf.    1.24849 (5) obj. -240861 iterations 14
Cbc0038I Pass  47: suminf.    0.95271 (3) obj. -240861 iterations 2
Cbc0038I Pass  48: suminf.    0.40952 (2) obj. -241615 iterations 3
Cbc0038I Pass  49: suminf.    0.37355 (2) obj. -240861 iterations 2
Cbc0038I Pass  50: suminf.    0.83814 (2) obj. -240861 iterations 2
Cbc0038I Pass  51: suminf.    0.33785 (2) obj. -240861 iterations 3
Cbc0038I Pass  52: suminf.    0.71447 (3) obj. -240861 iterations 5
Cbc0038I Pass  53: suminf.    0.43619 (2) obj. -241038 iterations 2
Cbc0038I Pass  54: suminf.    0.47604 (2) obj. -240861 iterations 2
Cbc0038I Pass  55: suminf.    0.78864 (3) obj. -240861 iterations 6
Cbc0038I Pass  56: suminf.    0.89619 (3) obj. -240861 iterations 3
Cbc0038I Pass  57: suminf.    0.71086 (2) obj. -240861 iterations 2
Cbc0038I Pass  58: suminf.    0.46629 (2) obj. -240861 iterations 3
Cbc0038I Pass  59: suminf.    0.50801 (3) obj. -240861 iterations 9
Cbc0038I Pass  60: suminf.    0.50801 (3) obj. -240861 iterations 0
Cbc0038I Pass  61: suminf.    0.55363 (2) obj. -240861 iterations 3
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 17 integers at bound fixed and 16 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 32 rows 31 columns
Cbc0038I Mini branch and bound improved solution from -240239 to -240885 (0.06 seconds)
Cbc0038I Round again with cutoff of -241624
Cbc0038I Reduced cost fixing fixed 15 variables on major pass 4
Cbc0038I Pass  61: suminf.    0.26140 (3) obj. -241624 iterations 1
Cbc0038I Pass  62: suminf.    0.66851 (2) obj. -241624 iterations 3
Cbc0038I Pass  63: suminf.    0.15286 (2) obj. -242505 iterations 1
Cbc0038I Pass  64: suminf.    0.14286 (1) obj. -242294 iterations 1
Cbc0038I Pass  65: suminf.    0.93612 (4) obj. -241624 iterations 7
Cbc0038I Pass  66: suminf.    0.16952 (2) obj. -241871 iterations 3
Cbc0038I Pass  67: suminf.    0.60622 (2) obj. -241624 iterations 4
Cbc0038I Pass  68: suminf.    0.60622 (2) obj. -241624 iterations 0
Cbc0038I Pass  69: suminf.    0.16952 (2) obj. -241871 iterations 3
Cbc0038I Pass  70: suminf.    0.59019 (3) obj. -241624 iterations 6
Cbc0038I Pass  71: suminf.    0.38165 (3) obj. -241624 iterations 2
Cbc0038I Pass  72: suminf.    0.33452 (2) obj. -242392 iterations 3
Cbc0038I Pass  73: suminf.    0.38165 (3) obj. -241624 iterations 3
Cbc0038I Pass  74: suminf.    0.30554 (3) obj. -241624 iterations 3
Cbc0038I Pass  75: suminf.    0.35774 (2) obj. -241624 iterations 4
Cbc0038I Pass  76: suminf.    0.15119 (2) obj. -241992 iterations 3
Cbc0038I Pass  77: suminf.    0.60160 (2) obj. -241624 iterations 4
Cbc0038I Pass  78: suminf.    0.60160 (2) obj. -241624 iterations 0
Cbc0038I Pass  79: suminf.    0.15119 (2) obj. -241992 iterations 3
Cbc0038I Pass  80: suminf.    0.86029 (2) obj. -241624 iterations 6
Cbc0038I Pass  81: suminf.    0.86029 (2) obj. -241624 iterations 1
Cbc0038I Pass  82: suminf.    0.37286 (2) obj. -242099 iterations 2
Cbc0038I Pass  83: suminf.    0.35021 (2) obj. -241624 iterations 2
Cbc0038I Pass  84: suminf.    0.86029 (2) obj. -241624 iterations 2
Cbc0038I Pass  85: suminf.    0.55771 (3) obj. -241624 iterations 7
Cbc0038I Pass  86: suminf.    0.55771 (3) obj. -241624 iterations 0
Cbc0038I Pass  87: suminf.    0.60575 (2) obj. -241624 iterations 1
Cbc0038I Pass  88: suminf.    0.42619 (2) obj. -242420 iterations 1
Cbc0038I Pass  89: suminf.    0.24619 (2) obj. -242659 iterations 5
Cbc0038I Pass  90: suminf.    0.53838 (2) obj. -241624 iterations 3
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 23 integers at bound fixed and 19 continuous
Cbc0038I Full problem 50 rows 64 columns, reduced to 14 rows 16 columns
Cbc0038I Mini branch and bound did not improve solution (0.08 seconds)
Cbc0038I After 0.08 seconds - Feasibility pump exiting with objective of -240885 - took 0.07 seconds
Cbc0012I Integer solution of -240885 found by feasibility pump after 0 iterations and 0 nodes (0.08 seconds)
Cbc0038I Full problem 50 rows 64 columns, reduced to 29 rows 32 columns
Cbc0031I 5 added rows had average density of 10
Cbc0013I At root node, 38 cuts changed objective from -243348.03 to -240885 in 6 passes
Cbc0014I Cut generator 0 (Probing) - 3 row cuts average 2.7 elements, 1 column cuts (1 active)  in 0.000 seconds - new frequency is 1
Cbc0014I Cut generator 1 (Gomory) - 23 row cuts average 20.3 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is 1
Cbc0014I Cut generator 2 (Knapsack) - 20 row cuts average 7.8 elements, 0 column cuts (0 active)  in 0.001 seconds - new frequency is 1
Cbc0014I Cut generator 3 (Clique) - 0 row cuts average 0.0 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is -100
Cbc0014I Cut generator 4 (MixedIntegerRounding2) - 7 row cuts average 19.0 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is 1
Cbc0014I Cut generator 5 (FlowCover) - 23 row cuts average 18.9 elements, 0 column cuts (0 active)  in 0.016 seconds - new frequency is 1
Cbc0014I Cut generator 6 (TwoMirCuts) - 48 row cuts average 15.9 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is 1
Cbc0001I Search completed - best objective -240885, took 49 iterations and 0 nodes (0.10 seconds)
Cbc0035I Maximum depth 0, 27 variables fixed on reduced cost
Cuts at root node changed objective from -243348 to -240885
Probing was tried 6 times and created 4 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
Gomory was tried 6 times and created 23 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
Knapsack was tried 6 times and created 20 cuts of which 0 were active after adding rounds of cuts (0.001 seconds)
Clique was tried 6 times and created 0 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
MixedIntegerRounding2 was tried 6 times and created 7 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
FlowCover was tried 6 times and created 23 cuts of which 0 were active after adding rounds of cuts (0.016 seconds)
TwoMirCuts was tried 6 times and created 48 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)

Result - Optimal solution found

Objective value:                240885.00000000
Enumerated nodes:               0
Total iterations:               49
Time (CPU seconds):             0.10
Time (Wallclock seconds):       0.10

Option for printingOptions changed from normal to all
Total time (CPU seconds):       0.11   (Wallclock seconds):       0.11
```
