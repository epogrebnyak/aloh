import pulp

from production import Machine, prod_and_cost


def test_prodcution_and_costs():
    plant = {
        "A": Machine(capacity=200, unit_cost=70),
        "B": Machine(capacity=100, unit_cost=40),
    }
    model = pulp.LpProblem("Test prod model", pulp.LpMaximize)
    prod, cost = prod_and_cost(plant, n_days=5)
    model += pulp.lpSum(prod)
    model.solve()
    assert [x.value() for x in prod["A"].values()] == [200] * 5
    assert [x.value() for x in cost["B"].values()] == [40 * 100] * 5
