from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver


class PartialOrderNoveltyMethodsOnlySolver(PartialOrderNoveltyMethodsSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue_action(self, model, novelty):
        """Add model to search queue after expanding an action"""
        self.search_models.novelty_add(model, 0)
