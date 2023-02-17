from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver


class PartialOrderNoveltyNoResetSolver(PartialOrderNoveltySolver):
    def __int__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        self.search_models.novelty_add(model, model.ranking)
