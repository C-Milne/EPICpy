from Solver.Heuristics.Heuristic import Heuristic


class SeenStatesPruning(Heuristic):
    def __int__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)

    def ranking(self, model) -> float:
        model_hash = hash((model.get_state(), tuple(model.get_task_network())))

        if model_hash in self._seen_states:
            return None
        self._seen_states.add(model_hash)
        return self._inner_ranking(model)

    def _inner_ranking(self, model):
        return 0

    def presolving_processing(self, **kwargs) -> None:
        pass

    def task_milestone(self, model) -> bool:
        return True
