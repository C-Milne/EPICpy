from Solver.Heuristics.Heuristic import Heuristic

"""This is a component to be used as part of other heuristic classes
Search can be initialised with multiple subtasks. After a model fully expands one subtask its current state is logged.
If another model completes the same subtask and has the same current state, it is pruned."""


class Pruning(Heuristic):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.seen_states = {}

    def ranking(self, model) -> float:
        return 0

    def presolving_processing(self, **kwargs) -> None:
        pass

    def task_milestone(self, model) -> bool:
        num_tasks_remaining = str(len(model.waiting_subtasks))
        if num_tasks_remaining not in self.seen_states:
            self.seen_states[num_tasks_remaining] = [self.solver.reproduce_state(model.current_state)]
            return True
        else:
            reproduced_state = self.solver.reproduce_state(model.current_state)
            if reproduced_state not in self.seen_states[num_tasks_remaining]:
                self.seen_states[num_tasks_remaining].append(reproduced_state)
                return True
            else:
                return False
