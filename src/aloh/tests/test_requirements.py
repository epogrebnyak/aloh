import numpy as np

from aloh.requirements import Materials

ms = Materials(["A", "B", "C"])
ms.require("A", 0.8, "B")
ms.require("A", 1, "C")
ms.require("B", 0.5, "C")


def test_B():
    assert (
        ms.B.to_numpy() == np.array([[0.0, 0.8, 1.0], [0.0, 0.0, 0.5], [0.0, 0.0, 0.0]])
    ).all()


def test_calculate_R():
    assert (
        ms.calculate_R()
        == np.array([[1.0, 0.8, 1.4], [0.0, 1.0, 0.5], [0.0, 0.0, 1.0]])
    ).all()


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


def test_ABC():
    ms = Materials(["A", "B", "C"])
    ms.require("A", 0.8, "B")
    ms.require("A", 1, "C")
    ms.require("B", 0.5, "C")
    assert ms.B.to_dict() == {
        "A": {"A": 0, "B": 0, "C": 0},
        "B": {"A": 0.8, "B": 0.0, "C": 0.0},
        "C": {"A": 1.0, "B": 0.5, "C": 0.0},
    }
    assert ms.R.to_dict() == {
        "A": {"A": 1.0, "B": 0.0, "C": 0.0},
        "B": {"A": 0.8, "B": 1.0, "C": 0.0},
        "C": {"A": 1.4, "B": 0.5, "C": 1.0},
    }


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
