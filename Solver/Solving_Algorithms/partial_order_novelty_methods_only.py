from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver


class PartialOrderNoveltyMethodsOnlySolver(PartialOrderNoveltyMethodsSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _create_initial_model(self, initial_state, subtasks, waiting_subtasks, progress_tracker_class):
        initial_model = self.ModelClass(initial_state, subtasks, self.problem, waiting_subtasks,
                                        progress_tracker_class=progress_tracker_class, initial_model=True)
        initial_model.current_state.initialise()
        return initial_model

    def _add_model_to_search_queue_action(self, model, novelty):
        """Add model to search queue after expanding an action"""
        self.search_models.novelty_add(model, 0)
