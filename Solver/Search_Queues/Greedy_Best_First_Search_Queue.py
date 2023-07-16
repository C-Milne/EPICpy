from Solver.Search_Queues.search_queue import SearchQueue


class GBFSSearchQueue(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
