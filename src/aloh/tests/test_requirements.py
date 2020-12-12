from requirements import Materials


def test_car_assembly():
    ps = ["car", "wheel", "body", "metal", "rubber"]
    ms = Materials(ps)
    ms.require("car", 1, "body")
    ms.require("car", 4, "wheel")
    ms.require("wheel", 10, "metal")
    ms.require("body", 1500, "metal")
    ms.require("body", 50, "rubber")
    ms.require("wheel", 7.5, "rubber")
    assert ms.R.loc["car", :].to_dict() == {
        "car": 1.0,
        "wheel": 4.0,
        "body": 1.0,
        "metal": 1540.0,
        "rubber": 80.0,
    }
