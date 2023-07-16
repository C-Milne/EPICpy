from Solver.Search_Queues.search_queue import SearchQueue
from Solver.Heuristics.landmarks import Landmarks


class SearchQueueGBFSDualLandmarks(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert 'domain' in kwargs
        assert 'problem' in kwargs
        assert 'solver' in kwargs
        self.Landmarks = Landmarks(kwargs['domain'], kwargs['problem'], kwargs['solver'], self)
        self.landmark_setup = False

    def _add_model(self, model):
        if not self.landmark_setup:
            self.Landmarks.presolving_processing(initial_model=model)
            self.landmark_setup = True

        res = self.heuristic.ranking(model)
        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue

        landmark_ranking = self.Landmarks.ranking(model)

        ranking = self._calc_ranking(model, res)
        model.set_ranking(ranking)
        model.set_secondary_ranking(landmark_ranking)

        self._Q.put(model)
        self._queue_size += 1

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
