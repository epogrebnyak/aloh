from orderbook import Order, make_accept_variables, get_shipment, get_sales
import pulp


def test_sales():
    order_dict = {
        "A": [
            Order(day=0, volume=160, price=10),
            Order(day=1, volume=120, price=10),
            Order(day=2, volume=140, price=10),
        ]
    }

    accept_dict = make_accept_variables(order_dict)
    ship = get_shipment(3, order_dict, accept_dict)
    sales = get_sales(3, order_dict, accept_dict)

    model = pulp.LpProblem("Test sales model", pulp.LpMaximize)
    model += pulp.lpSum(sales)
    model.solve()
    assert [x.value() for x in ship["A"]] == [160, 120, 140]
    assert [x.value() for x in sales["A"]] == [1600, 1200, 1400]
