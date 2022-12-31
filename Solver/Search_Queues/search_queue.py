from Solver.model import Model
from Internal_Representation.state import State
from Solver.Heuristics.Heuristic import Heuristic

"""
This SearchQueue ranks models using the A* principle (Cost thus far + estimated cost)
"""


class SearchQueue:
    def __init__(self):
        self._Q = []
        self._completed_models = []
        self.heuristic = None

    def add_heuristic(self, heuristic):
        assert isinstance(heuristic, Heuristic)
        self.heuristic = heuristic

    def add(self, model):
        if type(model) != Model:
            raise TypeError("Invalid parameter type!\n"
                            "Expected Model got {}".format(type(model)))

        if len(model.search_modifiers) > 0:
            self._add_model(model)
        elif len(model.search_modifiers) == 0 and len(model.waiting_subtasks) > 0:
            model.promote_waiting_subtask()
            if self.heuristic.task_milestone(model):
                self._add_model(model)
        else:
            self._add_completed_model(model)

    def _add_completed_model(self, model):
        self._completed_models.append(model)

    def _add_model(self, model):
        res = self.heuristic.ranking(model)
        ranking = model.get_progress_tracker().get_num_operations_taken() + res

        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue
        model.set_ranking(ranking)

        added = False
        i = 0
        while i < len(self._Q):
            if ranking < self._Q[i].get_ranking():
                self._Q.insert(i, model)
                added = True
                break
            i += 1
        if not added:
            self._Q.append(model)

    def clear_completed_models(self):
        self._completed_models = []

    def pop(self):
        if len(self._Q) == 0:
            return None
        return self._Q.pop(0)

    def clear(self):
        self._Q = []
        self._completed_models = []

    def get_num_search_models(self):
        return len(self._Q)

    def get_num_completed_models(self):
        return len(self._completed_models)

    def get_completed_models(self):
        return self._completed_models

    def __len__(self):
        return len(self._Q)
