# Пример (example1.py)

<https://github.com/epogrebnyak/aloh3/blob/main/example1.py>

```
Название модели: Two products model example1_py
Мы сохранили модель в файл two_products_model_example1_py.lp

Статус решения: Optimal

Период планирования, дней: 14

Мощности производства, тонн в день:
  A: 200
  B: 100

Заказы на продукт A
          day  volume  price  accepted
N заказа                              
0           0   120.0  123.9     False
1           1   280.0  168.6      True
2           3   180.0  132.2     False
3           3   280.0  161.5      True
4           4   160.0  169.1      True
5           4   140.0  157.0      True
6           4   260.0  150.2     False
7           4   120.0  162.7      True
8           5   240.0  124.3     False
9           7   100.0  177.5      True
10          7   100.0  122.6     False
11          7   160.0  171.6      True
12          7    60.0  124.0     False
13          8   260.0  148.0      True
14         10   100.0  179.2      True
15         10   220.0  122.0     False
16         11   240.0  167.7      True
17         11   140.0  129.8     False
18         11   260.0  179.7      True
19         13   180.0  151.3      True
20         13   180.0  124.8     False

Заказы на продукт B
          day  volume  price  accepted
N заказа                              
0           0   100.0  213.9     False
1           1   110.0  202.5     False
2           2   115.0  187.2     False
3           5    75.0  214.0      True
4           9    80.0  199.4      True
5           9    65.0  194.1     False
6           9    65.0  206.0     False
7          10    80.0  210.0      True
8          10    85.0  205.8     False
9          11   110.0  203.6     False
10         11    70.0  193.3     False
11         12    65.0  201.5      True
12         12   100.0  204.6      True

Спрос (тонн)
      Product.A  Product.B
день                      
0         120.0      100.0
1         280.0      110.0
2           0.0      115.0
3         460.0        0.0
4         680.0        0.0
5         240.0       75.0
6           0.0        0.0
7         420.0        0.0
8         260.0        0.0
9           0.0      210.0
10        320.0      165.0
11        640.0      180.0
12          0.0      165.0
13        360.0        0.0

Отгрузка (тонн)
      Product.A  Product.B
день                      
0           0.0        0.0
1         280.0        0.0
2           0.0        0.0
3         280.0        0.0
4         420.0        0.0
5           0.0       75.0
6           0.0        0.0
7         260.0        0.0
8         260.0        0.0
9           0.0       80.0
10        100.0       80.0
11        500.0        0.0
12          0.0      165.0
13        180.0        0.0

Производство (тонн)
      Product.A  Product.B
день                      
0         200.0        0.0
1         200.0        0.0
2         200.0        0.0
3         200.0        0.0
4         200.0        0.0
5         200.0       75.0
6         200.0        0.0
7         200.0        0.0
8         200.0        0.0
9         200.0       80.0
10        200.0       80.0
11        200.0       65.0
12        200.0      100.0
13        180.0        0.0

Запасы (тонн)
      Product.A  Product.B
день                      
0         200.0        0.0
1         120.0        0.0
2         320.0        0.0
3         240.0        0.0
4          20.0        0.0
5         126.2        0.0
6         326.2        0.0
7         266.2        0.0
8         206.2        0.0
9         306.2        0.0
10        306.2        0.0
11          6.2       65.0
12          0.0        0.0
13          0.0        0.0

Объемы мощностей, заказов, производства, покупок (тонн)
               Product.A  Product.B
capacity          2800.0     1400.0
orders            3780.0     1120.0
purchase          2280.0      400.0
internal_use       500.0        0.0
requirement       2780.0      400.0
production        2780.0      400.0
avg_inventory      174.5        4.6

Выручка (долл.США):  459158
Затраты (долл.США):  210600
Прибыль (долл.США):  248558

Целевая функция:     244794
```

### Работа солвера

```
Welcome to the CBC MILP Solver 
Version: 2.9.0 
Build Date: Feb 12 2015 

command line - D:\Anaconda3\lib\site-packages\pulp\apis\..\solverdir\cbc\win\64\cbc.exe C:\Users\B7E3~1\AppData\Local\Temp\63798052c104463da19f3f0edaf661ac-pulp.mps max ratio None allow None threads None presolve on strong None gomory on knapsack on probing on branch printingOptions all solution C:\Users\B7E3~1\AppData\Local\Temp\63798052c104463da19f3f0edaf661ac-pulp.sol (default strategy 1)
At line 2 NAME          MODEL
At line 3 ROWS
At line 56 COLUMNS
At line 1203 RHS
At line 1255 BOUNDS
At line 1318 ENDATA
Problem MODEL has 51 rows, 62 columns and 1016 elements
Coin0008I MODEL read with 0 errors
String of None is illegal for double parameter ratioGap value remains 0
String of None is illegal for double parameter allowableGap value remains 0
String of None is illegal for integer parameter threads value remains 0
String of None is illegal for integer parameter strongBranching value remains 5
Option for gomoryCuts changed from ifmove to on
Option for knapsackCuts changed from ifmove to on
Continuous objective value is 246966 - 0.00 seconds
Cgl0003I 0 fixed, 0 tightened bounds, 1 strengthened rows, 0 substitutions
Cgl0004I processed model has 49 rows, 62 columns (34 integer (34 of which binary)) and 942 elements
Cbc0038I Initial state - 4 integers unsatisfied sum - 0.312016
Cbc0038I Pass   1: suminf.    0.00000 (0) obj. -244370 iterations 5
Cbc0038I Solution found of -244370
Cbc0038I Relaxing continuous gives -244398
Cbc0038I Before mini branch and bound, 30 integers at bound fixed and 22 continuous
Cbc0038I Mini branch and bound did not improve solution (0.00 seconds)
Cbc0038I Round again with cutoff of -244655
Cbc0038I Reduced cost fixing fixed 14 variables on major pass 2
Cbc0038I Pass   2: suminf.    0.01331 (1) obj. -244655 iterations 2
Cbc0038I Pass   3: suminf.    0.07212 (1) obj. -245789 iterations 1
Cbc0038I Pass   4: suminf.    0.53365 (3) obj. -244655 iterations 3
Cbc0038I Pass   5: suminf.    1.17058 (3) obj. -244655 iterations 6
Cbc0038I Pass   6: suminf.    1.12047 (3) obj. -244655 iterations 1
Cbc0038I Pass   7: suminf.    0.82872 (3) obj. -244655 iterations 5
Cbc0038I Pass   8: suminf.    0.82872 (3) obj. -244655 iterations 0
Cbc0038I Pass   9: suminf.    1.12017 (3) obj. -244655 iterations 1
Cbc0038I Pass  10: suminf.    0.78753 (2) obj. -244655 iterations 1
Cbc0038I Pass  11: suminf.    0.78753 (2) obj. -244655 iterations 0
Cbc0038I Pass  12: suminf.    0.82872 (3) obj. -244655 iterations 3
Cbc0038I Pass  13: suminf.    0.82872 (3) obj. -244655 iterations 0
Cbc0038I Pass  14: suminf.    1.12017 (3) obj. -244655 iterations 1
Cbc0038I Pass  15: suminf.    0.78753 (2) obj. -244655 iterations 1
Cbc0038I Pass  16: suminf.    0.78753 (2) obj. -244655 iterations 0
Cbc0038I Pass  17: suminf.    0.82872 (3) obj. -244655 iterations 3
Cbc0038I Pass  18: suminf.    0.82872 (3) obj. -244655 iterations 0
Cbc0038I Pass  19: suminf.    1.12017 (3) obj. -244655 iterations 1
Cbc0038I Pass  20: suminf.    0.78753 (2) obj. -244655 iterations 1
Cbc0038I Pass  21: suminf.    0.78753 (2) obj. -244655 iterations 0
Cbc0038I Pass  22: suminf.    0.82872 (3) obj. -244655 iterations 3
Cbc0038I Pass  23: suminf.    0.82872 (3) obj. -244655 iterations 0
Cbc0038I Pass  24: suminf.    1.12017 (3) obj. -244655 iterations 1
Cbc0038I Pass  25: suminf.    0.78753 (2) obj. -244655 iterations 1
Cbc0038I Pass  26: suminf.    0.78753 (2) obj. -244655 iterations 0
Cbc0038I Pass  27: suminf.    0.82872 (3) obj. -244655 iterations 3
Cbc0038I Pass  28: suminf.    0.82872 (3) obj. -244655 iterations 0
Cbc0038I Pass  29: suminf.    1.12017 (3) obj. -244655 iterations 1
Cbc0038I Pass  30: suminf.    0.78753 (2) obj. -244655 iterations 1
Cbc0038I Pass  31: suminf.    0.78753 (2) obj. -244655 iterations 0
Cbc0038I No solution found this major pass
Cbc0038I Before mini branch and bound, 24 integers at bound fixed and 20 continuous
Cbc0038I Full problem 49 rows 62 columns, reduced to 13 rows 18 columns
Cbc0038I Mini branch and bound did not improve solution (0.02 seconds)
Cbc0038I After 0.02 seconds - Feasibility pump exiting with objective of -244398 - took 0.02 seconds
Cbc0012I Integer solution of -244398 found by feasibility pump after 0 iterations and 0 nodes (0.02 seconds)
Cbc0038I Full problem 49 rows 62 columns, reduced to 16 rows 26 columns
Cbc0031I 11 added rows had average density of 25.545455
Cbc0013I At root node, 11 cuts changed objective from -246966.2 to -244841.5 in 100 passes
Cbc0014I Cut generator 0 (Probing) - 7 row cuts average 2.0 elements, 0 column cuts (0 active)  in 0.017 seconds - new frequency is 1
Cbc0014I Cut generator 1 (Gomory) - 317 row cuts average 39.6 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is 1
Cbc0014I Cut generator 2 (Knapsack) - 56 row cuts average 7.6 elements, 0 column cuts (0 active)  in 0.031 seconds - new frequency is 1
Cbc0014I Cut generator 3 (Clique) - 0 row cuts average 0.0 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is -100
Cbc0014I Cut generator 4 (MixedIntegerRounding2) - 38 row cuts average 27.8 elements, 0 column cuts (0 active)  in 0.016 seconds - new frequency is 1
Cbc0014I Cut generator 5 (FlowCover) - 55 row cuts average 16.5 elements, 0 column cuts (0 active)  in 0.001 seconds - new frequency is 1
Cbc0014I Cut generator 6 (TwoMirCuts) - 91 row cuts average 20.3 elements, 0 column cuts (0 active)  in 0.045 seconds - new frequency is 1
Cbc0010I After 0 nodes, 1 on tree, -244398 best solution, best possible -244841.46 (0.18 seconds)
Cbc0012I Integer solution of -244794.38 found by DiveCoefficient after 918 iterations and 3 nodes (0.20 seconds)
Cbc0001I Search completed - best objective -244794.375, took 930 iterations and 4 nodes (0.20 seconds)
Cbc0032I Strong branching done 26 times (137 iterations), fathomed 0 nodes and fixed 1 variables
Cbc0035I Maximum depth 1, 24 variables fixed on reduced cost
Cuts at root node changed objective from -246966 to -244841
Probing was tried 109 times and created 7 cuts of which 0 were active after adding rounds of cuts (0.033 seconds)
Gomory was tried 109 times and created 322 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
Knapsack was tried 109 times and created 70 cuts of which 1 were active after adding rounds of cuts (0.031 seconds)
Clique was tried 100 times and created 0 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
MixedIntegerRounding2 was tried 109 times and created 44 cuts of which 0 were active after adding rounds of cuts (0.016 seconds)
FlowCover was tried 109 times and created 62 cuts of which 1 were active after adding rounds of cuts (0.001 seconds)
TwoMirCuts was tried 109 times and created 105 cuts of which 3 were active after adding rounds of cuts (0.045 seconds)

Result - Optimal solution found

Objective value:                244794.37500000
Enumerated nodes:               4
Total iterations:               930
Time (CPU seconds):             0.20
Time (Wallclock seconds):       0.20

Option for printingOptions changed from normal to all
Total time (CPU seconds):       0.23   (Wallclock seconds):       0.23
```