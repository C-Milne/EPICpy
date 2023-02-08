from Solver.Search_Queues.search_queue_newest_first import SearchQueueNewestFirst


class GBFSSearchQueueNewestFirst(SearchQueueNewestFirst):
    def __init__(self):
        super().__init__()

    def _calc_ranking(self, model, heuristic_estimate):
        return heuristic_estimate
