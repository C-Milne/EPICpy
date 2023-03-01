from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver


class PartialOrderNoveltyMethodsNoResetSolver(PartialOrderNoveltyMethodsSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method.
        When decomposing a task, this resets to 0"""
        method_novelty = self._check_method_novelty(addition)
        if method_novelty == 0:
            self.search_models.novelty_add(model, model.ranking * -1)
        else:
            self.search_models.novelty_add(model, max(method_novelty, model.ranking * -1))
