from Solver.Heuristics.hamming_distance import HammingDistance
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Internal_Representation.problem_predicate import ProblemPredicate


class HammingDistanceSeenStatesPruning(SeenStatesPruning, HammingDistance):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.goal_cons = []

    def _inner_ranking(self, model) -> float:
        return HammingDistance.ranking(self, model)

    def presolving_processing(self, **kwargs) -> None:
        HammingDistance.presolving_processing(self, **kwargs)
