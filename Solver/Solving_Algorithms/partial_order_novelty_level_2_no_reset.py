from Solver.Solving_Algorithms.partial_order_novelty_level_2 import PartialOrderNoveltyLevelTwoSolver
from Solver.Solving_Algorithms.partial_order_novelty_no_reset import PartialOrderNoveltyNoResetSolver


class PartialOrderNoveltyLevelTwoNoResetSolver(PartialOrderNoveltyLevelTwoSolver, PartialOrderNoveltyNoResetSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        PartialOrderNoveltyNoResetSolver._add_model_to_search_queue(self, model, addition)
