from Solver.Search_Queues.search_queue import SearchQueue


class GreedyCostSearchQueue(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _calc_ranking(self, model, heuristic_estimate):
        return model.get_num_operations_taken()/5 + heuristic_estimate
