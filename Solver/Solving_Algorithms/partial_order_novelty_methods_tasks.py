from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Internal_Representation.method import Method


class PartialOrderNoveltyMethodsTasksSolver(PartialOrderNoveltySolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self._seen_methods = set()
        self._seen_tasks = set()

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method."""
        novelty = self._check_addition_novelty(addition)
        self.search_models.novelty_add(model, novelty)

    def _check_addition_novelty(self, addition):
        novelty = 0
        added_mod = hash((addition.task, tuple(addition.given_params.values())))
        if type(addition.task) == Method:
            initial_size = len(self._seen_methods)
            self._seen_methods.add(added_mod)
            if initial_size < len(self._seen_methods):
                novelty = 1
                self.num_novel_methods += 1
            else:
                self.num_not_novel_methods += 1
        else:
            # Type of addition is abstract task
            initial_size = len(self._seen_tasks)
            self._seen_tasks.add(added_mod)
            if initial_size < len(self._seen_tasks):
                novelty = 1
        return novelty
