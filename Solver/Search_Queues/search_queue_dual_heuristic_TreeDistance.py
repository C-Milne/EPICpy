from Solver.Search_Queues.search_queue import SearchQueue
from Solver.Heuristics.tree_distance import TreeDistance


class SearchQueueGBFSDualTreeDistance(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert 'domain' in kwargs
        assert 'problem' in kwargs
        assert 'solver' in kwargs
        self.TreeDistance = TreeDistance(kwargs['domain'], kwargs['problem'], kwargs['solver'], self)
        self.tree_setup = False

    def _add_model(self, model):
        if not self.tree_setup:
            self.TreeDistance.presolving_processing()
            self.tree_setup = True

        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        tree_ranking = self.TreeDistance.ranking(model)

        ranking = self._calc_ranking(model, res)
        model.set_ranking(ranking)
        model.set_secondary_ranking(tree_ranking)

        self._Q.put(model)
        self._queue_size += 1

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
