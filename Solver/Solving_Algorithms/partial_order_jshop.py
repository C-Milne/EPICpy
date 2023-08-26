from partial_order import PartialOrderSolver


class PartialOrderJshopSolver(PartialOrderSolver):
    solvable_problem_types = ['jshop']

    def __init__(self, domain, problem):
        super().__init__(domain, problem)

