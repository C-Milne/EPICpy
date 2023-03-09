from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Internal_Representation.method import Method


class PartialOrderNoveltyMethodsSolver(PartialOrderNoveltySolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self._seen_methods = set()

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method.
        When decomposing a task, this resets to 0"""
        novelty = self._check_method_novelty(addition)
        self.search_models.novelty_add(model, novelty)

    def _check_method_novelty(self, addition):
        novelty = 0
        if type(addition.task) == Method:
            added_method = hash((addition.task, tuple(addition.given_params.values())))
            initial_size = len(self._seen_methods)
            self._seen_methods.add(added_method)
            if initial_size < len(self._seen_methods):
                novelty = 1
        return novelty
