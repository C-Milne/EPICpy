import sys
from Solver.Heuristics.partial_order_pruning import PartialOrderPruning
from Solver.Heuristics.tree_distance import Tree, TreeDistance
Task = sys.modules['Internal_Representation.task'].Task
Method = sys.modules['Internal_Representation.method'].Method
Action = sys.modules['Internal_Representation.action'].Action
Subtask = sys.modules['Internal_Representation.subtasks'].Subtask
Model = sys.modules["Solver.Models.default_model"].DefaultModel


class TreeDistancePartialOrder(PartialOrderPruning, TreeDistance):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.tree = Tree()

    def ranking(self, model: Model) -> float:
        return TreeDistance.ranking(self, model)

    def _calculate_distance_tasks(self, model: Model):
        return TreeDistance._calculate_distance_tasks(self, model)

    def presolving_processing(self, **kwargs) -> None:
        TreeDistance.presolving_processing(self)

    def _calculate_task_node_distance_goal(self, tn) -> int:
        return TreeDistance._calculate_task_node_distance_goal(self, tn)
