from Solver.Search_Queues.search_queue import SearchQueue


class GreedyCostSearchQueue(SearchQueue):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _add_model(self, model):
        res = self.heuristic.ranking(model)
        ranking = model.get_num_operations_taken()/5 + res

        if type(res) != int and (res is None or res == False):
            return  # Do not add to search queue
        model.set_ranking(ranking)

        added = False
        i = 0
        while i < len(self._Q):
            if ranking < self._Q[i].get_ranking():
                self._Q.insert(i, model)
                added = True
                break
            i += 1
        if not added:
            self._Q.append(model)
