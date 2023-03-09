from Solver.Heuristics.Heuristic import Heuristic

"""This is a component to be used as part of other heuristic classes
Search can be initialised with multiple subtasks. After a model fully expands one subtask its current state is logged.
If another model completes the same subtask and has the same current state, it is pruned."""


class PartialOrderPruning(Heuristic):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.seen_states = {}

    def ranking(self, model) -> float:
        return 0

    def presolving_processing(self, **kwargs) -> None:
        pass

    def task_milestone(self, model) -> bool:
        task_names = self._concat_remaining_tasks(model)
        if task_names not in self.seen_states:
            self.seen_states[task_names] = [self.solver.reproduce_state(model.current_state)]
            return True
        else:
            reproduced_state = self.solver.reproduce_state(model.current_state)
            if reproduced_state not in self.seen_states[task_names]:
                self.seen_states[task_names].append(reproduced_state)
                return True
            else:
                return False

    def _concat_remaining_tasks(self, model):
        task_names = model.get_search_modifier(0).task.name
        for p in model.get_search_modifier(0).parameters:
            task_names += p.name

        for w in model.waiting_subtasks:
            task_names += w.task.name
            for p in w.parameters:
                task_names += p.name
        return task_names
