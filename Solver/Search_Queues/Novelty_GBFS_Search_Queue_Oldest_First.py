from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue, Model


class NoveltyGBFSOldestFirstQueue(NoveltyGBFSQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
