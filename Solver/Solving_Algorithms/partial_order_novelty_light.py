import warnings
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver, Method
from Solver.Solving_Algorithms.solver import Solver
from Internal_Representation.state_novelty import StateNovelty
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning


class PartialOrderNoveltyLightSolver(PartialOrderNoveltySolver, Solver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self.max_novelty_level = 1

    def set_search_queue(self, search_queue):
        Solver.set_search_queue(self, search_queue)

    def _setup_set_heuristic(self):
        pass

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        # with open("Model_Tracking.txt", 'a') as f:
        #     f.write("Adding model to queue after method or task: {}\n".format(model.model_number))  # TODO: Remove this
        if type(addition.task) == Method:
            self._check_method_novelty(addition)
        self.search_models.add(model)

    def _add_model_to_search_queue_action(self, model, novelty):
        """Add model to search queue after expanding an action"""
        # with open("Model_Tracking.txt", 'a') as f:
        #     f.write("Adding model to queue after action: {}\n".format(model.model_number))  # TODO: Remove this
        self.search_models.add(model)
