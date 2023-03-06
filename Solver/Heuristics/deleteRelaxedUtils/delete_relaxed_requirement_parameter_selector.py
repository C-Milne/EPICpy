from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection


class DeleteRelaxedRequirementSelection(RequirementSelection):
    def __init__(self, solver):
        super().__init__(solver)

    def _check_object_satisfies_parameter_predicate_exists_check_not(self, model, pred, required_predicates, ob):
        indexes = model.current_state.get_indexes(pred)
        indexes_inverse = model.current_state.get_indexes('not_' + pred)
        if indexes_inverse:
            for index in indexes_inverse:
                if self._compare_object_to_fact(index, required_predicates[pred] - 1, ob, model):
                    return True
        if indexes is None:
            return True
        for index in indexes:
            if self._compare_object_to_fact(index, required_predicates[pred] - 1, ob, model):
                return False
        return True
