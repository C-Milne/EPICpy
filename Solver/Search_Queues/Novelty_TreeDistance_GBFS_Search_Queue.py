from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue


class NoveltyTreeDistanceGBFSSearchQueue(NoveltyGBFSQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _add_model_novelty(self, model, novelty):
        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        if novelty:
            self.num_novel_states += 1
            ranking = -1
        else:
            self.num_not_novel_states += 1
            ranking = 0

        model.set_ranking(ranking)
        model.set_secondary_ranking(res)

        self._Q.put(model)
        self._queue_size += 1
