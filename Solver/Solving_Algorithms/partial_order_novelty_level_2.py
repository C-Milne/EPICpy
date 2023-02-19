from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver


class PartialOrderNoveltyLevelTwoSolver(PartialOrderNoveltySolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self.max_novelty_level = 2
