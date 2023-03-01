from Solver.Search_Queues.search_queue import SearchQueue, Model


class NoveltyGBFSOldestFirstQueue(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_novel_states = 0
        self.num_not_novel_states = 0

    def novelty_add(self, model, novelty):
        if not isinstance(model, Model):
            raise TypeError("Invalid parameter type!\n"
                            "Expected Model got {}".format(type(model)))

        if len(model.search_modifiers) > 0:
            self._add_model_novelty(model, novelty)
        elif len(model.search_modifiers) == 0 and len(model.waiting_subtasks) > 0:
            model.promote_waiting_subtask()
            if self.heuristic.task_milestone(model):
                self._add_model_novelty(model, novelty)
        else:
            self._add_completed_model(model)

    def _add_model_novelty(self, model, novelty):
        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        if novelty > 0:
            self.num_novel_states += 1
            ranking = -1 * novelty  # We do this since we adjust the novelty scores from the state novelty class
            # i.e. when max level = 2, a new fact gets score 2 and new pair get score 1
        else:
            self.num_not_novel_states += 1
            ranking = novelty

        model.set_ranking(ranking)
        model.set_secondary_ranking(self._total_added_models)

        self._Q.put(model)
        self._total_added_models += 1
        self._queue_size += 1
