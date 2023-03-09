import warnings
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
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

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        self.search_models.add(model)

    def _add_model_to_search_queue_action(self, model, novelty):
        """Add model to search queue after expanding an action"""
        self.search_models.add(model)
