from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection


class DeleteRelaxedRequirementSelection(RequirementSelection):
    def __init__(self, solver):
        super().__init__(solver)
