import pulp


def lst(xs):
    return ", ".join(xs)


def print_solvers():
    """
    Информация по солверам.

    Дополнительные ссылки:
    - https://github.com/coin-or/Cbc
    - https://en.wikipedia.org/wiki/Branch_and_cut
    - https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html
    """
    print("\nВозможные солверы:", lst(pulp.list_solvers()))
    print("Доступные:  ", lst(pulp.list_solvers(onlyAvailable=True)))
    default_solver = pulp.LpSolverDefault  # 'PULP_CBC_CMD'
    print("Использован:", default_solver.name)
    print("Где находится:", pulp.get_solver(default_solver.name).path)
