from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver, Method


class PartialOrderNoveltyMethodsNoResetSolver(PartialOrderNoveltyMethodsSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method.
        When decomposing a task, this stays with the models current novelty score
        When decomposing a method we check if the method is novel. If not we keep the current novelty score"""

        novelty = self._check_addition_novelty(model, addition)
        self.search_models.novelty_add(model, novelty)

    def _check_addition_novelty(self, model, addition):
        if type(addition.task) == Method:
            method_novelty = self._check_method_novelty(addition)
            current_novelty = model.ranking * -1
            if method_novelty > 0 and current_novelty > 0:
                self._num_novel_methods_novel_state += 1
            else:
                self._num_novel_method_not_novel_state += 1
            return max(method_novelty, current_novelty)
        else:
            return model.ranking * -1
