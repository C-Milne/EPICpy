from Solver.Heuristics.Heuristic import Heuristic

"""This is a simple intuitive method of breadth first search.
Simply giving priority to search models which have executed the least operations (tasks, method, and actions).
This is essentially the same search strategy as 'breadth_first_by_actions' but better at handling infinite recursion"""


class NoPruning(Heuristic):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)

    def ranking(self, model) -> float:
        return 0

    def presolving_processing(self, **kwargs) -> None:
        pass

    def task_milestone(self, model) -> bool:
        return True
