from Solver.Solving_Algorithms.partial_order_hamming_novelty import PartialOrderHammingNoveltySolver


class PartialOrderHammingNoveltyNoResetSolver(PartialOrderHammingNoveltySolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        self.search_models.heu_novelty_add(model, model.secondary_ranking * -1, None)
