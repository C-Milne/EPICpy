from Solver.Search_Queues.search_queue import SearchQueue


class SearchQueueNewestFirst(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _add_model(self, model):
        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        ranking = self._calc_ranking(model, res)
        model.set_ranking(ranking)
        model.set_queue_location(self._total_added_models)

        self._Q.put(model)
        self._total_added_models -= 1
        self._queue_size += 1
