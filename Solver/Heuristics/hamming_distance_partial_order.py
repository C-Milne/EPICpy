from Solver.Heuristics.partial_order_pruning import PartialOrderPruning
from Solver.Heuristics.hamming_distance import HammingDistance
from Internal_Representation.problem_predicate import ProblemPredicate

"""This is based on the idea of Hamming Distance. https://www.sciencedirect.com/topics/engineering/hamming-distance"""


class HammingDistancePartialOrder(PartialOrderPruning, HammingDistance):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.goal_cons = []

    def ranking(self, model) -> float:
        return HammingDistance.ranking(self, model)

    def presolving_processing(self, **kwargs) -> None:
        HammingDistance.presolving_processing(self, **kwargs)
