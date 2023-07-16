from queue import PriorityQueue
from Solver.Models.model import Model
from Solver.Heuristics.Heuristic import Heuristic

"""
This SearchQueue ranks models using the A* principle (Cost thus far + estimated cost)
"""


class SearchQueue:
    # TODO: Turn this into a ABC class
    def __init__(self, **kwargs):
        self._Q = PriorityQueue()
        self._completed_models = []
        self.heuristic = None
        self._queue_size = 0
        self._total_added_models = 0

    def add_heuristic(self, heuristic):
        assert isinstance(heuristic, Heuristic)
        self.heuristic = heuristic

    def add(self, model):
        if not isinstance(model, Model):
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
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        ranking = self._calc_ranking(model, res)
        model.set_ranking(ranking)
        model.set_secondary_ranking(self._total_added_models)

        self._Q.put(model)
        self._total_added_models += 1
        self._queue_size += 1

    def _calc_ranking(self, model, heuristic_estimate):
        return model.get_progress_tracker().get_num_operations_taken() + heuristic_estimate

    def clear_completed_models(self):
        self._completed_models = []

    def pop(self):
        if self._queue_size == 0:
            return None
        self._queue_size -= 1
        return self._Q.get()

    def clear(self):
        self._Q = PriorityQueue()
        self._completed_models = []

    def get_num_search_models(self):
        # TODO : Remove this function (use len instead)
        return len(self)

    def get_num_completed_models(self):
        return len(self._completed_models)

    def get_completed_models(self):
        return self._completed_models

    def get_model_list(self):
        return self._Q.queue

    def __len__(self):
        return self._queue_size
