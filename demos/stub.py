import pulp  # type: ignore

LpExpression = pulp.pulp.LpAffineExpression


def foo() -> LpExpression:
    return pulp.lpSum(0)


"""
D:\github\aloh3 (main -> origin)
λ mypy stub.py
stub.py:5: error: Variable "stub.LpExpression" is not valid as a type
stub.py:5: note: See https://mypy.readthedocs.io/en/latest/common_issues.html#variables-vs-type-aliases
Found 1 error in 1 file (checked 1 source file)
"""
