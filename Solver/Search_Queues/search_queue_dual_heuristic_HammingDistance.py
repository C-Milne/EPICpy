from Solver.Search_Queues.search_queue import SearchQueue
from Solver.Heuristics.hamming_distance import HammingDistance


class SearchQueueGBFSDualHammingDistance(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert 'domain' in kwargs
        assert 'problem' in kwargs
        assert 'solver' in kwargs
        self.HammingDistance = HammingDistance(kwargs['domain'], kwargs['problem'], kwargs['solver'], self)
        self.hamming_setup = False

    def _add_model(self, model):
        if not self.hamming_setup:
            self.HammingDistance.presolving_processing()
            self.hamming_setup = True

        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        hamming_ranking = self.HammingDistance.ranking(model)

        ranking = self._calc_ranking(model, res)
        model.set_ranking(ranking)
        model.set_secondary_ranking(hamming_ranking)

        self._Q.put(model)
        self._queue_size += 1

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
