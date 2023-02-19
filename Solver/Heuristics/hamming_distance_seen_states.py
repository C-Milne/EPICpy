from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Internal_Representation.problem_predicate import ProblemPredicate


class HammingDistanceSeenStatesPruning(SeenStatesPruning):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.goal_cons = []

    def _inner_ranking(self, model) -> float:
        # Consider distance to goal
        distance_to_goal = 0
        for i in self.goal_cons:
            if i not in model.current_state.elements:
                distance_to_goal += 1
        return distance_to_goal

    def presolving_processing(self) -> None:
        if self.problem.goal_conditions is not None:
            for i in self.problem.goal_conditions.conditions:
                if type(i) == list:
                    if len(i) == 1:
                        self.goal_cons.append(ProblemPredicate(self.domain.get_predicate(i[0]), []))
                    else:
                        obs = [self.problem.get_object(x) for x in i[1:]]
                        self.goal_cons.append(ProblemPredicate(self.domain.get_predicate(i[0]), obs))
