from Solver.Search_Queues.search_queue import SearchQueue


class GBFSSearchQueue(SearchQueue):
    def __init__(self):
        super().__init__()

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
