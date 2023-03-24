from Solver.Search_Queues.search_queue import SearchQueue, Model


class HeuNoveltyGBFSQueue(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def heu_novelty_add(self, model, novelty, heuristic_val):
        if not isinstance(model, Model):
            raise TypeError("Invalid parameter type!\n"
                            "Expected Model got {}".format(type(model)))

        if heuristic_val is None:
            heuristic_val = self.heuristic.ranking(model)

        if len(model.search_modifiers) > 0:
            self._add_model_heu_novelty(model, novelty, heuristic_val)
        elif len(model.search_modifiers) == 0 and len(model.waiting_subtasks) > 0:
            model.promote_waiting_subtask()
            if self.heuristic.task_milestone(model):
                self._add_model_heu_novelty(model, novelty, heuristic_val)
        else:
            self._add_completed_model(model)

    def _add_model_heu_novelty(self, model, novelty, heuristic_val):
        if type(heuristic_val) != int and (heuristic_val is None or heuristic_val == False):
            return  # Do not add to search queue

        if novelty > 0:
            ranking = -1 * novelty  # We do this since we adjust the novelty scores from the state novelty class
            # i.e. when max level = 2, a new fact gets score 2 and new pair get score 1
        else:
            ranking = novelty

        model.set_ranking(heuristic_val)
        model.set_secondary_ranking(ranking)
        model.set_queue_location(self._total_added_models)

        self._Q.put(model)
        self._total_added_models -= 1
        self._queue_size += 1
