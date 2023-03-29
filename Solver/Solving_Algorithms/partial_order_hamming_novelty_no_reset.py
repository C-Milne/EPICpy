from Solver.Solving_Algorithms.partial_order_hamming_novelty import PartialOrderHammingNoveltySolver, Method


class PartialOrderHammingNoveltyNoResetSolver(PartialOrderHammingNoveltySolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self.num_novel_methods_novel_state = 0
        self.num_novel_method_not_novel_state = 0

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        if type(addition.task) == Method:
            method_novelty = self._check_method_novelty(addition)
            current_novelty = model.secondary_ranking * -1
            if method_novelty > 0:
                if current_novelty > 0:
                    self.num_novel_methods_novel_state += 1
                else:
                    self.num_novel_method_not_novel_state += 1
        self.search_models.heu_novelty_add(model, model.secondary_ranking * -1, None)
